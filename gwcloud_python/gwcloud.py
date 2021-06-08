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

    def start_bilby_job(self, job_name, job_description, private, ini_string):
        """Submit the parameters required to start a Bilby job

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
                    result
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

        return self.client.request(query=query, variables=variables)

    def get_preferred_job_list(self):
        """Get list of public Bilby jobs corresponding to a search of "preferred" and a time_range of "Any time"

        Returns
        -------
        list
            List of BilbyJob instances
        """
        return self._get_public_jobs(search="preferred", time_range="Any time")

    def _get_job_model_from_query(self, query_data):
        return BilbyJob(client=self, **rename_dict_keys(query_data, [('id', 'job_id')]))

    def _get_public_jobs(self, search="", time_range="Any time", number=100):
        query = """
            query ($search: String, $timeRange: String, $first: Int){
                publicBilbyJobs (search: $search, timeRange: $timeRange, first: $first) {
                    edges {
                        node {
                            id
                            user
                            name
                            description
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

        data, errors = self.client.request(query=query, variables=variables)

        return [self._get_job_model_from_query(job['node']) for job in data['publicBilbyJobs']['edges']]

    def _get_job_by_id(self, job_id):
        query = """
            query ($id: ID!){
                bilbyJob (id: $id) {
                    id
                    name
                    userId
                    description
                }
            }
        """

        variables = {
            "id": job_id
        }

        data, errors = self.client.request(query=query, variables=variables)

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
                        }
                    }
                }
            }
        """
        
        data, errors = self.client.request(query=query)

        return [self._get_job_model_from_query(job['node']) for job in data['bilbyJobs']['edges']]

    def _get_files_by_job_id(self, job_id):
        query = """
            query ($jobId: ID!) {
                bilbyResultFiles (jobId: $jobId) {
                    files {
                        path
                        isDir
                        fileSize
                        downloadId
                    }
                }
            }
        """

        variables = {
            "jobId": job_id
        }

        data, errors = self.client.request(query=query, variables=variables)

        file_list = []
        for f in data['bilbyResultFiles']['files']:
            if f['isDir']:
                continue
            f['path'] = remove_path_anchor(Path(f['path']))
            file_list.append(f)

        return file_list

    def _get_file_by_id(self, file_id):
        download_url = GWCLOUD_FILE_DOWNLOAD_ENDPOINT + str(file_id)
        request = requests.get(download_url)
        return request.content

    def _get_files_by_id(self, file_ids):
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            files = executor.map(self._get_file_by_id, file_ids)
            for i, f in enumerate(files):
                logger.info(f'File {i+1} of {len(file_ids)} downloaded!')

        return files
