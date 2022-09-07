import os
import tarfile
from pathlib import Path
from tempfile import NamedTemporaryFile
import itertools
from contextlib import ExitStack

from gwdc_python import GWDC
from gwdc_python.files import FileReference, FileReferenceList
from gwdc_python.helpers import TimeRange, Cluster
from gwdc_python.utils import rename_dict_keys
from gwdc_python.logger import create_logger

from .bilby_job import BilbyJob
from .event_id import EventID
from .exceptions import custom_error_handler
from .utils.file_download import _download_files, _save_file_map_fn, _get_file_map_fn
from .utils.file_upload import check_file
from .settings import GWCLOUD_ENDPOINT, GWCLOUD_AUTH_ENDPOINT

logger = create_logger(__name__)


class GWCloud:
    """
    GWCloud class provides an API for interacting with Bilby, allowing jobs to be submitted and acquired.

    Parameters
    ----------
    token : str
        API token for a Bilby user
    auth_endpoint : str, optional
        URL to which we send the authentication queries, by default GWCLOUD_AUTH_ENDPOINT
    endpoint : str, optional
        URL to which we send the queries, by default GWCLOUD_ENDPOINT

    Attributes
    ----------
    client : GWDC
        Handles a lot of the underlying logic surrounding the queries
    """
    def __init__(self, token="", auth_endpoint=GWCLOUD_AUTH_ENDPOINT, endpoint=GWCLOUD_ENDPOINT):
        self.client = GWDC(
            token=token,
            auth_endpoint=auth_endpoint,
            endpoint=endpoint,
            custom_error_handler=custom_error_handler
        )
        self.request = self.client.request  # Setting shorthand for simplicity

    def _upload_supporting_files(self, tokens, file_paths):
        """
        Uploads supporting files for a job

        Parameters
        ----------
        token : list
            List of supporting file upload tokens
        file_path : list
            List of local file paths to the supporting files to be uploaded

        Returns
        -------
        None
        """
        query = """
            mutation SupportingFilesUploadMutation($input: UploadSupportingFilesMutationInput!) {
                uploadSupportingFiles(input: $input) {
                    result {
                        result
                    }
                }
            }
        """
        file_paths = map(check_file, file_paths)
        with ExitStack() as stack:
            files = [stack.enter_context(file_path.open('rb')) for file_path in file_paths]

            variables = {
                "input": {
                    "supportingFiles": [
                        {"fileToken": token, "supportingFile": f} for token, f in zip(tokens, files)
                    ]
                }
            }

            data = self.request(query=query, variables=variables, authorize=False)

        result = data['upload_supporting_files']['result']['result']
        if not result:
            raise Exception("Unable to upload supporting files. An error occurred on the remote side.")

    def start_bilby_job_from_string(self, job_name, job_description, private, ini_string, cluster=Cluster.DEFAULT):
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
        cluster : ~gwdc_python.helpers.Cluster or str
            The name of the cluster to submit the job to

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
                        supportingFiles {
                            filePath
                            token
                        }
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
                        "private": private,
                        "cluster": cluster.value if isinstance(cluster, Cluster) else cluster
                    },
                    "iniString": {
                        "iniString": str(ini_string)
                    }
                },
            }
        }

        data = self.request(query=query, variables=variables)

        # Upload any supporting files returned by the job submission
        tokens, file_paths = [], []
        for supporting_file in data['new_bilby_job_from_ini_string']['result']['supporting_files']:
            tokens.append(supporting_file['token'])
            file_paths.append(supporting_file['file_path'])

        self._upload_supporting_files(tokens, file_paths)

        job_id = data['new_bilby_job_from_ini_string']['result']['job_id']
        return self.get_job_by_id(job_id)

    def start_bilby_job_from_file(self, job_name, job_description, private, ini_file, cluster=Cluster.DEFAULT):
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
        cluster : ~gwdc_python.helpers.Cluster or str
            The name of the cluster to submit the job to

        Returns
        -------
        str
            Message received from server after job submission
        """

        # Change the working directory to the folder containing the ini file, this will make the supporting file upload
        # search for files relative to the ini file
        cwd = Path().resolve()
        ini_file = Path(ini_file)
        try:
            os.chdir(Path(ini_file).parent)
            with ini_file.open() as f:
                ini_string = f.read().strip()
                return self.start_bilby_job_from_string(job_name, job_description, private, ini_string, cluster)
        finally:
            os.chdir(str(cwd))

    def get_preferred_job_list(self, search=""):
        """Get list of public Bilby jobs corresponding to a search of "preferred" and a time_range of "Any time"

        Parameters
        ----------
        search : str, optional
            Search terms by which to filter public job list, by default ""

        Returns
        -------
        list
            List of BilbyJob instances for the preferred jobs corresponding to the search terms
        """
        return self.get_public_job_list(search=f"preferred lasky {search}", time_range=TimeRange.ANY)

    def _get_job_model_from_query(self, query_data):
        if not query_data:
            return None
        return BilbyJob(
            client=self,
            **rename_dict_keys(
                query_data,
                {'id': 'job_id'}
            )
        )

    def get_public_job_list(self, search="", time_range=TimeRange.ANY, number=100):
        """Obtains a list of public Bilby jobs, filtering based on the search terms
        and the time range within which the job was created.

        Parameters
        ----------
        search : str, optional
            Search terms by which to filter public job list, by default ""
        time_range : ~gwdc_python.helpers.TimeRange or str, optional
            Time range by which to filter job list, by default TimeRange.ANY
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
                            eventId {
                                eventId
                                triggerId
                                nickname
                                isLigoEvent
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "search": search,
            "timeRange": time_range.value if isinstance(time_range, TimeRange) else time_range,
            "first": number
        }

        data = self.request(query=query, variables=variables)

        if not data['public_bilby_jobs']['edges']:
            logger.info('Job search returned no results.')
            return []

        return [self._get_job_model_from_query(job['node']) for job in data['public_bilby_jobs']['edges']]

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
                    user
                    description
                    jobStatus {
                        name
                        date
                    }
                    eventId {
                        eventId
                        triggerId
                        nickname
                        isLigoEvent
                    }
                }
            }
        """

        variables = {
            "id": job_id
        }

        data = self.request(query=query, variables=variables)

        if not data['bilby_job']:
            logger.info('No job matching input ID was returned.')
            return None

        return self._get_job_model_from_query(data['bilby_job'])

    def get_user_jobs(self, number=100):
        """Obtains a list of Bilby jobs created by the user, filtering based on the search terms
        and the time range within which the job was created.

        Parameters
        ----------
        number : int, optional
            Number of job results to return in one request, by default 100

        Returns
        -------
        list
            List of BilbyJob instances for the jobs corresponding to the search terms and in the specified time range
        """
        query = """
            query ($first: Int){
                bilbyJobs (first: $first){
                    edges {
                        node {
                            id
                            name
                            user
                            description
                            jobStatus {
                                name
                                date
                            }
                            eventId {
                                eventId
                                triggerId
                                nickname
                                isLigoEvent
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "first": number
        }

        data = self.request(query=query, variables=variables)

        return [self._get_job_model_from_query(job['node']) for job in data['bilby_jobs']['edges']]

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
                    isUploadedJob
                }
            }
        """

        variables = {
            "jobId": job_id
        }

        data = self.request(query=query, variables=variables)
        uploaded = data['bilby_result_files']['is_uploaded_job']

        file_list = FileReferenceList()
        for file_data in data['bilby_result_files']['files']:
            if file_data['is_dir']:
                continue
            file_data.pop('is_dir')
            file_list.append(
                FileReference(
                    **file_data,
                    job_id=job_id,
                    uploaded=uploaded
                )
            )

        return file_list, uploaded

    def get_files_by_reference(self, file_references):
        """Obtains file data when provided a :class:`~gwdc_python.files.file_reference.FileReferenceList`

        Parameters
        ----------
        file_references : ~gwdc_python.files.file_reference.FileReferenceList
            Contains the :class:`~gwdc_python.files.file_reference.FileReference` objects for which
            to download the contents

        Returns
        -------
        list
            List of tuples containing the file path and file contents as a byte string
        """
        batched = file_references.batched

        file_ids = [
            self._get_download_ids_from_tokens(job_id, job_files.get_tokens())
            for job_id, job_files in batched.items()
        ]

        file_ids = list(itertools.chain.from_iterable(file_ids))
        batched_files = FileReferenceList(list(itertools.chain.from_iterable(batched.values())))

        file_paths = batched_files.get_paths()
        file_uploaded = batched_files.get_uploaded()
        total_size = batched_files.get_total_bytes()

        files = _download_files(_get_file_map_fn, file_ids, file_paths, file_uploaded, total_size)

        logger.info(f'All {len(file_ids)} files downloaded!')

        return files

    def save_files_by_reference(self, file_references, root_path, preserve_directory_structure=True):
        """Save files when provided a :class:`~gwdc_python.files.file_reference.FileReferenceList` and a root path

        Parameters
        ----------
        file_references : ~gwdc_python.files.file_reference.FileReferenceList
            Contains the :class:`~gwdc_python.files.file_reference.FileReference` objects for which
            to save the associated files
        root_path : str or ~pathlib.Path
            Directory into which to save the files
        preserve_directory_structure : bool, optional
            Remove any directory structure for the downloaded files, by default True
        """
        batched = file_references.batched

        file_ids = [
            self._get_download_ids_from_tokens(job_id, job_files.get_tokens())
            for job_id, job_files in batched.items()
        ]

        file_ids = list(itertools.chain.from_iterable(file_ids))
        batched_files = FileReferenceList(list(itertools.chain.from_iterable(batched.values())))

        file_paths = batched_files.get_output_paths(root_path, preserve_directory_structure)
        file_uploaded = batched_files.get_uploaded()
        total_size = batched_files.get_total_bytes()

        _download_files(_save_file_map_fn, file_ids, file_paths, file_uploaded, total_size)

        logger.info(f'All {len(file_ids)} files saved!')

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

        data = self.request(query=query, variables=variables)

        return data['generate_file_download_ids']['result']

    def _generate_upload_token(self):
        """Creates a new long lived upload token for use uploading jobs

        Returns
        -------
        str
            The upload token
        """
        query = """
            query GenerateBilbyJobUploadToken {
                generateBilbyJobUploadToken {
                  token
                }
            }
        """

        data = self.request(query=query)
        return data['generate_bilby_job_upload_token']['token']

    def upload_job_archive(self, description, job_archive, public=False):
        """Upload a bilby job to GWCloud by job output archive

        Parameters
        ----------
        description : str
            The description of the job to add to the database

        public : bool
            If the uploaded job should be public or not

        job_archive : str
            The path to the job output archive to upload

        Returns
        -------
        BilbyJob
            The created Bilby job
        """
        query = """
            mutation JobUploadMutation($input: UploadBilbyJobMutationInput!) {
                uploadBilbyJob(input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        with open(job_archive, 'rb') as f:
            variables = {
                "input": {
                    "uploadToken": self._generate_upload_token(),
                    "details": {
                        "description": description,
                        "private": not public
                    },
                    "jobFile": f
                }
            }

            data = self.request(query=query, variables=variables, authorize=False)

        job_id = data['upload_bilby_job']['result']['job_id']
        return self.get_job_by_id(job_id)

    def upload_job_directory(self, description, job_directory, public=False):
        """Upload a bilby job to GWCloud by job output directory

        Parameters
        ----------
        description : str
            The description of the job to add to the database

        public : bool
            If the uploaded job should be public or not

        job_directory : str
            The path to the job output directory to upload

        Returns
        -------
        BilbyJob
            The created Bilby job
        """

        # Generate a temporary archive of the job
        path = Path(job_directory)
        with NamedTemporaryFile(dir=job_directory, suffix='.tar.gz') as f:
            with tarfile.open(f.name, "w:gz", compresslevel=2) as tar_handle:
                for item in path.rglob("*"):
                    print(item)
                    tar_handle.add(item, arcname=item.relative_to(path), recursive=False)

            # Upload the archive
            return self.upload_job_archive(description, f.name, public)

    def create_event_id(self, event_id, gps_time, trigger_id=None, nickname=None, is_ligo_event=False):
        """Create an Event ID that can be assigned to Bilby Jobs

        **INFO**:
        *Event IDs can only be created by a select few users.*

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456
        gps_time : float
            The GPS time that this Event ID represents, e.g. 1126259462.391
        trigger_id : str, optional
            Trigger ID of the event, must be of the form S123456a, by default None
        nickname : str, optional
            Common name used to identify the event, by default None
        is_ligo_event : bool, optional
            Should the event be visible to ligo users only, by default False

        Returns
        -------
        .EventID
            The created Event ID
        """
        query = """
            mutation CreateEventIDMutation($input: EventIDMutationInput!) {
                createEventId (input: $input) {
                    result
                }
            }
        """
        variables = {
            "input": {
                "eventId": event_id,
                "triggerId": trigger_id,
                "nickname": nickname,
                "isLigoEvent": is_ligo_event,
                "gpsTime": gps_time,
            }
        }
        data = self.request(query=query, variables=variables)
        logger.info(data['create_event_id']['result'])
        return self.get_event_id(event_id=event_id)

    def update_event_id(self, event_id, gps_time=None, trigger_id=None, nickname=None, is_ligo_event=None):
        """Create an Event ID that can be assigned to Bilby Jobs

        **INFO**:
        *Event IDs can only be updated by a select few users.*

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456
        gps_time : float, optional
            The GPS time that this Event ID represents, e.g. 1126259462.391
        trigger_id : str, optional
            Trigger ID of the event, must be of the form S123456a, by default None
        nickname : str, optional
            Common name used to identify the event, by default None
        is_ligo_event : bool, optional
            Should the event be visible to ligo users only, by default None

        Returns
        -------
        .EventID
            The updated Event ID
        """
        query = """
            mutation UpdateEventIDMutation($input: UpdateEventIDMutationInput!) {
                updateEventId (input: $input) {
                    result
                }
            }
        """
        variables = {
            "input": {
                "eventId": event_id,
                "triggerId": trigger_id,
                "nickname": nickname,
                "isLigoEvent": is_ligo_event,
                "gpsTime": gps_time,
            }
        }
        data = self.request(query=query, variables=variables)
        logger.info(data['update_event_id']['result'])
        return self.get_event_id(event_id=event_id)

    def delete_event_id(self, event_id):
        """Delete an Event ID

        **INFO**:
        *Event IDs can only be deleted by a select few users.*

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456
        """
        query = """
            mutation DeleteEventIDMutation($input: DeleteEventIDMutationInput!) {
                deleteEventId (input: $input) {
                    result
                }
            }
        """
        variables = {
            "input": {
                "eventId": event_id
            }
        }
        data = self.request(query=query, variables=variables)
        logger.info(data['delete_event_id']['result'])

    def get_event_id(self, event_id):
        """Get EventID by the event_id

        Parameters
        ----------
        event_id : str
            Event ID of the form GW123456_123456

        Returns
        -------
        .EventID
            The requested Event ID
        """
        query = """
            query ($eventId: String!){
                eventId (eventId: $eventId) {
                    eventId
                    triggerId
                    nickname
                    isLigoEvent
                    gpsTime
                }
            }
        """
        if event_id == '':
            return None

        variables = {
            "eventId": event_id
        }
        data = self.request(query=query, variables=variables)
        return EventID(**data['event_id'])

    def get_all_event_ids(self):
        """Obtain a list of all Event IDs

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456

        Returns
        -------
        list
            A list of all .EventID objects
        """
        query = """
            query {
                allEventIds {
                    eventId
                    triggerId
                    nickname
                    isLigoEvent
                    gpsTime
                }
            }
        """
        data = self.request(query=query)
        return [EventID(**event) for event in data['all_event_ids']]
