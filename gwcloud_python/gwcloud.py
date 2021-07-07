import requests
import concurrent.futures
import logging
from pathlib import Path
from gwdc_python import GWDC

from .bilby_job import BilbyJob
from .utils import remove_path_anchor, rename_dict_keys

GWCLOUD_ENDPOINT = 'https://gwcloud.org.au/bilby/graphql'
GWCLOUD_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/job/apiv1/file/?fileId='

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class GWCloud:
    """
    GWCloud class provides an API for interacting with Bilby, allowing jobs to be submitted and acquired.

    Parameters
    ----------
    token : str
        API token for a Bilby user
    endpoint : str, optional
            URL to which we send the queries, by default GWCLOUD_ENDPOINT

    Attributes
    ----------
    client : GWDC
        Handles a lot of the underlying logic surrounding the queries
    """
    def __init__(self, token, endpoint=GWCLOUD_ENDPOINT):
        self.client = GWDC(token=token, endpoint=endpoint)

    def start_bilby_job_from_string(self, job_name, job_description, private, ini_string):
        """Submit the parameters required to start a Bilby job, using the contents of an .ini file

        Parameters
        ----------
        job_name : str
            Name of the job to be created
        job_description : str
            Description of the job to be created
        private : bool
            True if job should be private, False if public
        ini_string : str
            The contents of a Bilby ini file

        Returns
        -------
        str
            Message received from server after job submission
        """
        query = """
            mutation NewBilbyJobFromIniString($input: BilbyJobFromIniStringMutationInput!){
                newBilbyJobFromIniString (input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        variables = {
            "input": {
                "params": {
                    "details": {
                        "name": job_name,
                        "description": job_description,
                        "private": private
                    },
                    "iniString": {
                        "iniString": ini_string
                    }
                },
            }
        }

        data = self.client.request(query=query, variables=variables)
        job_id = data['newBilbyJobFromIniString']['result']['jobId']
        return self.get_job_by_id(job_id)

    def start_bilby_job_from_file(self, job_name, job_description, private, ini_file):
        """Submit the parameters required to start a Bilby job, using an .ini file

        Parameters
        ----------
        job_name : str
            Name of the job to be created
        job_description : str
            Description of the job to be created
        private : bool
            True if job should be private, False if public
        ini_file : str or Path
            Path to an .ini file for running a Bilby job

        Returns
        -------
        str
            Message received from server after job submission
        """
        ini_file = Path(ini_file)
        with ini_file.open() as f:
            ini_string = f.read().strip()
            return self.start_bilby_job_from_string(job_name, job_description, private, ini_string)

    def get_preferred_job_list(self):
        """Get list of public Bilby jobs corresponding to a search of "preferred" and a time_range of "Any time"

        Returns
        -------
        list
            List of BilbyJob instances
        """
        return self.get_public_job_list(search="preferred lasky", time_range="Any time")

    def _get_job_model_from_query(self, query_data):
        return BilbyJob(client=self, **rename_dict_keys(query_data, [('id', 'job_id'), ('jobStatus', 'job_status')]))

    def get_public_job_list(self, search="", time_range="Any time", number=100):
        """Obtains a list of public Bilby jobs, filtering based on the search terms
        and the time range within which the job was created.

        Parameters
        ----------
        search : str, optional
            Search terms by which to fileter public job list, by default ""
        time_range : str, optional
            Time range by which to filter job list, by default "Any time"
        number : int, optional
            Number of job results to return in one request, by default 100

        Returns
        -------
        list
            List of BilbyJob instances for the jobs corresponding to the search terms and in the specified time range
        """
        query = """
            query ($search: String, $timeRange: String, $first: Int){
                publicBilbyJobs (search: $search, timeRange: $timeRange, first: $first) {
                    edges {
                        node {
                            id
                            user
                            name
                            description
                            jobStatus {
                                name
                                date
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "search": search,
            "timeRange": time_range,
            "first": number
        }

        data = self.client.request(query=query, variables=variables)

        return [self._get_job_model_from_query(job['node']) for job in data['publicBilbyJobs']['edges']]

    def get_job_by_id(self, job_id):
        """Get a Bilby job instance corresponding to a specific job ID

        Parameters
        ----------
        job_id : str
            ID of job to obtain

        Returns
        -------
        BilbyJob
            BilbyJob instance corresponding to the input ID
        """
        query = """
            query ($id: ID!){
                bilbyJob (id: $id) {
                    id
                    name
                    userId
                    description
                    jobStatus {
                        name
                        date
                    }
                }
            }
        """

        variables = {
            "id": job_id
        }

        data = self.client.request(query=query, variables=variables)

        return self._get_job_model_from_query(data['bilbyJob'])

    def _get_user_jobs(self):
        query = """
            query {
                bilbyJobs {
                    edges {
                        node {
                            id
                            name
                            userId
                            description
                            jobStatus {
                                name
                                date
                            }
                        }
                    }
                }
            }
        """
        
        data = self.client.request(query=query)

        return [self._get_job_model_from_query(job['node']) for job in data['bilbyJobs']['edges']]

    def _get_files_by_job_id(self, job_id):
        query = """
            query ($jobId: ID!) {
                bilbyResultFiles (jobId: $jobId) {
                    files {
                        path
                        isDir
                        fileSize
                        downloadToken
                    }
                }
            }
        """

        variables = {
            "jobId": job_id
        }

        data = self.client.request(query=query, variables=variables)

        file_list = []
        for f in data['bilbyResultFiles']['files']:
            if f['isDir']:
                continue
            f.pop('isDir')
            f['path'] = remove_path_anchor(Path(f['path']))
            file_list.append(f)

        return file_list

    def _get_file_by_id(self, file_id):
        download_url = GWCLOUD_FILE_DOWNLOAD_ENDPOINT + str(file_id)
        request = requests.get(download_url)
        return request.content

    def _get_files_by_id(self, file_ids):
        result = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            files = executor.map(self._get_file_by_id, file_ids)
            for i, f in enumerate(files):
                logger.info(f'File {i+1} of {len(file_ids)} downloaded! Filesize: {len(f)}')
                result.append(f)

        return result

    def _get_download_id_from_token(self, job_id, file_token):
        """Get a single file download id for a file download token

        Parameters
        ----------
        job_id : str
            Job id which owns the file token

        file_token : str
            Download token for the desired file

        Returns
        -------
        str
            Download id for the desired file
        """
        return self._get_download_ids_from_tokens(job_id, [file_token])[0]

    def _get_download_ids_from_tokens(self, job_id, file_tokens):
        """Get many file download ids for a list of file download tokens

        Parameters
        ----------
        job_id : str
            Job id which owns the file token

        file_tokens : list
            Download tokens for the desired files

        Returns
        -------
        list
            List of download ids for the desired files
        """
        query = """
            mutation ResultFileMutation($input: GenerateFileDownloadIdsInput!) {
                generateFileDownloadIds(input: $input) {
                    result
                }
            }
        """

        variables = {
            "input": {
                "jobId": job_id,
                "downloadTokens": file_tokens
            }
        }

        data = self.client.request(query=query, variables=variables)

        return data['generateFileDownloadIds']['result']
