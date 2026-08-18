import json
import os
import tarfile
from contextlib import ExitStack
from pathlib import Path
from tempfile import NamedTemporaryFile
import itertools

import requests
from gwdc_python import GWDC
from gwdc_python.files import FileReference, FileReferenceList
from gwdc_python.helpers import TimeRange, Cluster
from gwdc_python.utils import rename_dict_keys
from gwdc_python.logger import create_logger

from .bilby_job import BilbyJob
from .event_id import EventID
from .exceptions import custom_error_handler, GWCloudException
from .gwflow_pending_file import GWFlowPendingFile
from .gwflow_job_upsert_result import GWFlowJobUpsertResult
from .gwflow_job import GWFlowJob
from .utils.file_download import _download_files, _save_file_map_fn, _get_file_map_fn
from .utils.file_upload import check_file
from .settings import (
    GWCLOUD_ENDPOINT,
    GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT,
    GWCLOUD_FILE_DOWNLOAD_TIMEOUT,
)

logger = create_logger(__name__)


class GWCloud:
    """
    GWCloud class provides an API for interacting with Bilby, allowing jobs to be submitted and acquired.

    Parameters
    ----------
    token : str, optional
        API token for a Bilby user. If omitted, creates an anonymous read-only GWCloud instance
    endpoint : str, optional
        URL to which we send the queries, by default GWCLOUD_ENDPOINT

    Attributes
    ----------
    client : GWDC
        Handles a lot of the underlying logic surrounding the queries
    """

    def __init__(self, token="", endpoint=GWCLOUD_ENDPOINT):
        self.client = GWDC(
            token=token,
            endpoint=endpoint,
            custom_error_handler=custom_error_handler,
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

    def get_official_job_list(self, search=""):
        """Get list of public Bilby jobs corresponding to a search of "labels.name:Official" and
        a time_range of "Any time"

        Parameters
        ----------
        search : str, optional
            Search terms by which to filter public job list, by default ""

        Returns
        -------
        list
            List of BilbyJob instances for the official jobs corresponding to the search terms
        """
        return self.get_public_job_list(search=f"labels.name:Official {search}", time_range=TimeRange.ANY)

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

    def _get_files_by_bilby_job(self, job):
        query = """
            query ($jobId: ID!) {
                bilbyResultFiles (jobId: $jobId) {
                    files {
                        path
                        isDir
                        fileSize
                        downloadToken
                    }
                    jobType
                }
            }
        """

        variables = {
            "jobId": job.id
        }

        data = self.request(query=query, variables=variables)
        job.type = data['bilby_result_files']['job_type']

        file_list = FileReferenceList()
        for file_data in data['bilby_result_files']['files']:
            if file_data['is_dir']:
                continue
            file_data.pop('is_dir')
            file_list.append(
                FileReference(
                    **file_data,
                    parent=job
                )
            )
        return file_list

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

        files = _download_files(_get_file_map_fn, file_ids, batched_files)
        file_dict = {key: val for key, val in files}

        logger.info(f'All {len(file_ids)} files downloaded!')

        return [(ref.path, file_dict[ref.path]) for ref in file_references]

    def save_files_by_reference(self, file_references, root_path):
        """Save files when provided a :class:`~gwdc_python.files.file_reference.FileReferenceList` and a root path

        Parameters
        ----------
        file_references : ~gwdc_python.files.file_reference.FileReferenceList
            Contains the :class:`~gwdc_python.files.file_reference.FileReference` objects for which
            to save the associated files
        root_path : str or ~pathlib.Path
            Directory into which to save the files
        """
        batched = file_references.batched

        file_ids = [
            self._get_download_ids_from_tokens(job_id, job_files.get_tokens())
            for job_id, job_files in batched.items()
        ]

        file_ids = list(itertools.chain.from_iterable(file_ids))
        batched_files = FileReferenceList(list(itertools.chain.from_iterable(batched.values())))

        _download_files(_save_file_map_fn, file_ids, batched_files, root_path)

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
                    tar_handle.add(item, arcname=item.relative_to(path), recursive=False)

            # Upload the archive
            return self.upload_job_archive(description, f.name, public)

    def upload_external_job(self, job_name, job_description, private, ini_string, url):
        """Upload a Bilby job to GWCloud with external results

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
        url : str
            The URL to the external results. Might be a url directly to a result file, or to a directory listing, or
            something else

        Returns
        -------
        BilbyJob
            The created Bilby job
        """
        query = """
            mutation UploadExternalBilbyJob($input: UploadExternalBilbyJobMutationInput!) {
                uploadExternalBilbyJob(input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        variables = {
            "input": {
                "details": {
                    "name": job_name,
                    "description": job_description,
                    "private": private
                },
                "iniFile": ini_string,
                "resultUrl": url
            }
        }

        data = self.request(query=query, variables=variables)

        job_id = data['upload_external_bilby_job']['result']['job_id']
        return self.get_job_by_id(job_id)

    def upload_hdf5_job(self, description, hdf5_file, ini_file, public=False):
        """Upload a bilby job to GWCloud with HDF5 result file and INI configuration file

        Parameters
        ----------
        description : str
            The description of the job to add to the database
        hdf5_file : str
            The path to the HDF5 result file
        ini_file : str
            The path to the INI configuration file
        public : bool
            If the uploaded job should be public or not

        Returns
        -------
        BilbyJob
            The created Bilby job
        """
        query = """
            mutation JobUploadMutation($input: UploadHdf5BilbyJobMutationInput!) {
                uploadHdf5BilbyJob(input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        with open(hdf5_file, 'rb') as hdf5_f, open(ini_file, 'rb') as ini_f:
            variables = {
                "input": {
                    "uploadToken": self._generate_upload_token(),
                    "details": {
                        "description": description,
                        "private": not public
                    },
                    "hdf5File": hdf5_f,
                    "iniFile": ini_f
                }
            }

            data = self.request(query=query, variables=variables, authorize=False)

        job_id = data['upload_hdf5_bilby_job']['result']['job_id']
        return self.get_job_by_id(job_id)

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

    @staticmethod
    def _format_gwflow_files(files):
        """Convert a list of file dicts from snake_case to the camelCase shape expected by the server.

        Parameters
        ----------
        files : list of dict
            Each dict may use snake_case keys (``analysis_uid``, ``file_name``, ``file_size``,
            ``md5_sum``) or camelCase equivalents.

        Returns
        -------
        list of dict
            Dicts with camelCase keys ready to include in the GraphQL variables.
        """
        formatted = []
        for f in files:
            ff = {}
            analysis_uid = f.get('analysis_uid') or f.get('analysisUid')
            if analysis_uid is not None:
                ff['analysisUid'] = analysis_uid
            path = f.get('path')
            if path is not None:
                ff['path'] = path
            file_name = f.get('file_name') or f.get('fileName')
            if file_name is not None:
                ff['fileName'] = file_name
            file_size = f['file_size'] if 'file_size' in f else f.get('fileSize')
            if file_size is not None:
                ff['fileSize'] = file_size
            md5_sum = f.get('md5_sum') or f.get('md5Sum')
            if md5_sum is not None:
                ff['md5Sum'] = md5_sum
            formatted.append(ff)
        return formatted

    def upsert_gwflow_job(
        self, sname, *, schema_version=None, metadata=None,
        libraries=None, is_pruned=None, ligo_only=None,
        event_id=None, current_history_id=None,
        current_history_timestamp=None, files=None
    ) -> 'GWFlowJobUpsertResult':
        """Upsert a GWFlow job record (transactional get-or-create by sname).

        Parameters
        ----------
        sname : str
            Super-name of the job
        schema_version : str, optional
            Version of the schema, by default None
        metadata : dict, optional
            Metadata dictionary for the job; serialised to JSON before sending, by default None
        libraries : list, optional
            List of library names, by default None
        is_pruned : bool, optional
            Whether the job is pruned, by default None
        ligo_only : bool, optional
            Whether the job is LIGO only, by default None
        event_id : str, optional
            Event ID associated with the job, by default None
        current_history_id : str, optional
            ID of the current history record, by default None
        current_history_timestamp : str or datetime, optional
            Timestamp of the current history record (ISO 8601 or datetime), by default None
        files : list of dict, optional
            Files to register; each dict may use snake_case keys (``analysis_uid``,
            ``file_name``, ``file_size``, ``md5_sum``) or their camelCase equivalents,
            by default None

        Returns
        -------
        GWFlowJobUpsertResult
            The result of the upsert operation
        """
        query = """
            mutation UpsertGwflowJob($input: UpsertGwflowJobMutationInput!) {
                upsertGwflowJob(input: $input) {
                    result {
                        gwflowJobId
                        sname
                        created
                        filesPending { id sname analysisUid path fileName md5Sum }
                    }
                }
            }
        """

        params = {"sname": sname}
        if schema_version is not None:
            params["schemaVersion"] = schema_version
        if metadata is not None:
            params["metadata"] = json.dumps(metadata)
        if libraries is not None:
            params["libraries"] = libraries
        if is_pruned is not None:
            params["isPruned"] = is_pruned
        if ligo_only is not None:
            params["ligoOnly"] = ligo_only
        if event_id is not None:
            params["eventId"] = event_id
        if current_history_id is not None:
            params["currentHistoryId"] = current_history_id
        if current_history_timestamp is not None:
            if hasattr(current_history_timestamp, 'isoformat'):
                params["currentHistoryTimestamp"] = current_history_timestamp.isoformat()
            else:
                params["currentHistoryTimestamp"] = current_history_timestamp
        if files is not None:
            params["files"] = self._format_gwflow_files(files)

        variables = {"input": {"params": params}}
        data = self.request(query=query, variables=variables)
        result_data = data['upsert_gwflow_job']['result']

        files_pending = [GWFlowPendingFile.from_dict(f) for f in (result_data.get('files_pending') or [])]

        return GWFlowJobUpsertResult(
            job_id=result_data['gwflow_job_id'],
            sname=result_data['sname'],
            created=result_data['created'],
            files_pending=files_pending
        )

    def upload_gwflow_file(self, gwflow_file_id: str, file_path) -> int:
        """
        Upload a file for a GWFlow job.

        Parameters
        ----------
        gwflow_file_id : str
            Relay global ID of the GWFlow file to upload
        file_path : str or Path
            Local path to the file to upload

        Returns
        -------
        int
            Size of the uploaded file
        """
        query = """
            mutation UploadGwflowFile($input: UploadGwflowFileMutationInput!) {
                uploadGwflowFile(input: $input) {
                    result { success fileSize }
                }
            }
        """
        file_path = check_file(file_path)
        with open(file_path, 'rb') as f:
            variables = {
                "input": {
                    "gwflowFileId": gwflow_file_id,
                    "file": f
                }
            }
            data = self.request(query=query, variables=variables)

        result = data['upload_gwflow_file']['result']
        if not result['success']:
            raise Exception("Failed to upload GWFlow file.")
        return int(result['file_size'])

    def get_gwflow_pending_files(self) -> 'list[GWFlowPendingFile]':
        """
        Get all not-yet-mirrored GWFlow files.

        Returns
        -------
        list
            List of pending GWFlow files
        """
        query = """
            query {
                gwflowPendingFiles { id sname analysisUid path fileName md5Sum }
            }
        """
        data = self.request(query=query)
        return [GWFlowPendingFile.from_dict(f) for f in data.get('gwflow_pending_files', [])]

    def link_bilby_job_to_gwflow(self, job_id: str, sname: str, analysis_uid: str) -> None:
        """Link a Bilby job to a GWFlow analysis.

        Parameters
        ----------
        job_id : str
            Relay global ID of the BilbyJob
        sname : str
            Super-name of the GWFlow job to link to. Pass an empty string ``""`` to
            unlink the Bilby job from its current GWFlow analysis.
        analysis_uid : str
            Unique identifier of the analysis
        """
        query = """
            mutation LinkBilbyJobToGwflow($input: LinkBilbyJobToGwflowMutationInput!) {
                linkBilbyJobToGwflow(input: $input) {
                    result { success }
                }
            }
        """
        variables = {
            "input": {
                "jobId": job_id,
                "sname": sname,
                "analysisUid": analysis_uid
            }
        }
        data = self.request(query=query, variables=variables)
        if not data['link_bilby_job_to_gwflow']['result']['success']:
            raise Exception("Failed to link Bilby job to GWFlow.")

    def get_gwflow_job_list(self, search="", time_range="all", include_pruned=False) -> 'list[GWFlowJob]':
        """Get a list of GWFlow jobs, paging through all results

        Parameters
        ----------
        search : str, optional
            Search terms by which to filter the job list, by default ""
        time_range : str, optional
            Time range by which to filter the job list, by default "all"
        include_pruned : bool, optional
            Whether to include pruned jobs in the results, by default False

        Returns
        -------
        list
            List of GWFlowJob instances for the jobs matching the search terms
        """
        query = """
            query GwflowJobs($search: String, $timeRange: String, $includePruned: Boolean,
                             $cursor: ID, $count: Int) {
                gwflowJobs(search: $search, timeRange: $timeRange,
                           includePruned: $includePruned, cursor: $cursor, count: $count) {
                    edges { node { id sname schemaVersion libraries isPruned ligoOnly
                                   currentHistoryId currentHistoryTimestamp lastUpdated
                                   eventId { eventId triggerId nickname gpsTime } }
                          cursor }
                    pageInfo { hasNextPage endCursor }
                }
            }
        """

        jobs = []
        cursor = None
        count = 100
        variables = {
            "search": search,
            "timeRange": time_range,
            "includePruned": include_pruned,
            "count": count
        }
        while True:
            if cursor is not None:
                variables["cursor"] = cursor

            data = self.request(query=query, variables=variables)
            gwflow_jobs = data['gwflow_jobs']
            jobs.extend(GWFlowJob.from_dict(edge['node']) for edge in gwflow_jobs['edges'])
            page_info = gwflow_jobs['page_info']
            if not page_info['has_next_page']:
                break
            end_cursor = page_info['end_cursor']
            if end_cursor is None or end_cursor == cursor:
                break
            cursor = end_cursor

        return jobs

    def get_gwflow_job(self, sname) -> 'GWFlowJob | None':
        """Get a GWFlow job instance corresponding to a specific super-name (sname)

        Parameters
        ----------
        sname : str
            Super-name of the job to obtain

        Returns
        -------
        GWFlowJob or None
            GWFlowJob instance corresponding to the input sname, or None if no such job exists
        """
        query = """
            query GwflowJobBySname($sname: String!) {
                gwflowJobBySname(sname: $sname) {
                    id sname schemaVersion libraries isPruned ligoOnly currentHistoryId
                    currentHistoryTimestamp creationTime lastUpdated
                    eventId { eventId triggerId nickname gpsTime }
                    files { id analysisUid path fileName fileSize uploaded downloadToken }
                    bilbyJobs { id name gwflowAnalysisUid }
                }
            }
        """

        variables = {
            "sname": sname
        }

        data = self.request(query=query, variables=variables)

        if not data['gwflow_job_by_sname']:
            return None

        return GWFlowJob.from_dict(data['gwflow_job_by_sname'])

    def download_gwflow_file(self, download_token: str, output_path) -> None:
        """Download a GWFlow file to a local path

        Parameters
        ----------
        download_token : str
            Download token for the file to download
        output_path : str or Path
            Local path to which to save the file
        """
        download_url = GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT + download_token
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with requests.get(download_url, stream=True, timeout=GWCLOUD_FILE_DOWNLOAD_TIMEOUT) as request:
            if request.status_code == 404:
                raise GWCloudException(
                    "File not found or not available for download (404). "
                    "It may be a ligo_only record or a not-yet-mirrored file."
                )
            if request.status_code != 200:
                raise GWCloudException(
                    f"Failed to download GWFlow file: HTTP {request.status_code}."
                )
            with output_path.open("wb") as f:
                for chunk in request.iter_content(chunk_size=1024 * 16):
                    f.write(chunk)
