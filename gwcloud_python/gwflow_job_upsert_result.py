from dataclasses import dataclass
from typing import List

from .gwflow_pending_file import GWFlowPendingFile


@dataclass
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
    job_id: str
    sname: str
    created: bool
    files_pending: List[GWFlowPendingFile]
