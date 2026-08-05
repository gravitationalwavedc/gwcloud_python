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
