class GWFlowPendingFile:
    """
    GWFlowPendingFile class stores information about files pending upload for a GWFlow job.

    Parameters
    ----------
    id : str
        Global ID for the pending file record
    sname : str
        Super-name (sname) of the job
    analysis_uid : str
        Unique identifier for the analysis
    path : str
        Path of the file relative to the analysis root
    file_name : str
        Name of the file
    md5_sum : str, optional
        MD5 checksum of the file, by default None
    """
    def __init__(self, id, sname, analysis_uid, path, file_name, md5_sum=None):
        self.id = id
        self.sname = sname
        self.analysis_uid = analysis_uid
        self.path = path
        self.file_name = file_name
        self.md5_sum = md5_sum

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            sname=d.get('sname'),
            analysis_uid=d.get('analysisUid') or d.get('analysis_uid'),
            path=d.get('path'),
            file_name=d.get('fileName') or d.get('file_name'),
            md5_sum=d.get('md5Sum') or d.get('md5_sum'),
        )


class GWFlowJobUpsertResult:
    """
    GWFlowJobUpsertResult class stores the result of upserting a GWFlow job.

    Parameters
    ----------
    job_id : str
        Global ID for the upserted job
    sname : str
        Super-name (sname) of the job
    created : bool
        True if the job was newly created, False if it was updated
    files_pending : list
        List of files that still need to be uploaded
    """
    def __init__(self, job_id, sname, created, files_pending):
        self.job_id = job_id
        self.sname = sname
        self.created = created
        self.files_pending = files_pending


class GWFlowFile:
    """
    GWFlowFile class stores information about a file belonging to a GWFlow job.

    Parameters
    ----------
    id : str
        Global ID for the file record
    analysis_uid : str
        Unique identifier for the analysis
    path : str
        Path of the file relative to the analysis root
    file_name : str
        Name of the file
    file_size : int
        Size of the file in bytes
    uploaded : bool
        True if the file has been uploaded, False otherwise
    download_token : str
        Token used to download the file
    """
    def __init__(self, id, analysis_uid, path, file_name, file_size, uploaded, download_token):
        self.id = id
        self.analysis_uid = analysis_uid
        self.path = path
        self.file_name = file_name
        self.file_size = file_size
        self.uploaded = uploaded
        self.download_token = download_token

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            analysis_uid=d.get('analysisUid') or d.get('analysis_uid'),
            path=d.get('path'),
            file_name=d.get('fileName') or d.get('file_name'),
            file_size=d.get('fileSize') if 'fileSize' in d else d.get('file_size'),
            uploaded=d.get('uploaded'),
            download_token=d.get('downloadToken') or d.get('download_token'),
        )


class GWFlowLinkedBilbyJob:
    """
    GWFlowLinkedBilbyJob class stores information about a bilby job linked to a GWFlow job.

    Parameters
    ----------
    id : str
        Global ID for the bilby job
    name : str
        Name of the bilby job
    gwflow_analysis_uid : str
        Unique identifier of the linked GWFlow analysis
    """
    def __init__(self, id, name, gwflow_analysis_uid):
        self.id = id
        self.name = name
        self.gwflow_analysis_uid = gwflow_analysis_uid

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            name=d.get('name'),
            gwflow_analysis_uid=d.get('gwflowAnalysisUid') or d.get('gwflow_analysis_uid'),
        )


class GWFlowEventID:
    """
    GWFlowEventID class stores information about the event associated with a GWFlow job.

    Parameters
    ----------
    event_id : str
        Global ID for the event
    trigger_id : str
        Identifier of the event trigger
    nickname : str
        Nickname of the event
    gps_time : float
        GPS time of the event
    """
    def __init__(self, event_id, trigger_id, nickname, gps_time):
        self.event_id = event_id
        self.trigger_id = trigger_id
        self.nickname = nickname
        self.gps_time = gps_time

    @classmethod
    def from_dict(cls, d):
        return cls(
            event_id=d.get('eventId') or d.get('event_id'),
            trigger_id=d.get('triggerId') or d.get('trigger_id'),
            nickname=d.get('nickname'),
            gps_time=d.get('gpsTime') if 'gpsTime' in d else d.get('gps_time'),
        )


class GWFlowJob:
    """
    GWFlowJob class stores information about a GWFlow job.

    Parameters
    ----------
    id : str
        Global ID for the job
    sname : str
        Super-name (sname) of the job
    schema_version : str
        Version of the job schema
    libraries : str
        Libraries used by the job
    is_pruned : bool
        True if the job has been pruned, False otherwise
    ligo_only : bool
        True if the job is LIGO-only, False otherwise
    current_history_id : str
        Global ID of the current history entry
    current_history_timestamp : str
        Timestamp of the current history entry
    last_updated : str
        Timestamp of the last update
    creation_time : str, optional
        Timestamp of creation, by default None
    event_id : GWFlowEventID, optional
        Event associated with the job, by default None
    files : list
        List of GWFlowFile instances, by default []
    bilby_jobs : list
        List of GWFlowLinkedBilbyJob instances, by default []
    """
    def __init__(self, id, sname, schema_version, libraries, is_pruned, ligo_only,
                 current_history_id, current_history_timestamp, last_updated,
                 creation_time=None, event_id=None, files=None, bilby_jobs=None):
        self.id = id
        self.sname = sname
        self.schema_version = schema_version
        self.libraries = libraries
        self.is_pruned = is_pruned
        self.ligo_only = ligo_only
        self.current_history_id = current_history_id
        self.current_history_timestamp = current_history_timestamp
        self.last_updated = last_updated
        self.creation_time = creation_time
        self.event_id = event_id
        self.files = files if files is not None else []
        self.bilby_jobs = bilby_jobs if bilby_jobs is not None else []

    @classmethod
    def from_dict(cls, d):
        event_id = d.get('eventId') or d.get('event_id')
        return cls(
            id=d.get('id'),
            sname=d.get('sname'),
            schema_version=d.get('schemaVersion') or d.get('schema_version'),
            libraries=d.get('libraries'),
            is_pruned=d.get('isPruned') if 'isPruned' in d else d.get('is_pruned'),
            ligo_only=d.get('ligoOnly') if 'ligoOnly' in d else d.get('ligo_only'),
            current_history_id=d.get('currentHistoryId') or d.get('current_history_id'),
            current_history_timestamp=d.get('currentHistoryTimestamp') or d.get('current_history_timestamp'),
            last_updated=d.get('lastUpdated') or d.get('last_updated'),
            creation_time=d.get('creationTime') or d.get('creation_time'),
            event_id=GWFlowEventID.from_dict(event_id) if event_id else None,
            files=[GWFlowFile.from_dict(f) for f in (d.get('files') or [])],
            bilby_jobs=[GWFlowLinkedBilbyJob.from_dict(j) for j in (d.get('bilbyJobs') or d.get('bilby_jobs') or [])],
        )
