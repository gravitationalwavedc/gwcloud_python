from dataclasses import dataclass, field
from typing import List, Optional

from .gwflow_event_id import GWFlowEventID
from .gwflow_file import GWFlowFile
from .gwflow_linked_bilby_job import GWFlowLinkedBilbyJob


@dataclass
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
    id: str
    sname: str
    schema_version: str
    libraries: str
    is_pruned: bool
    ligo_only: bool
    current_history_id: str
    current_history_timestamp: str
    last_updated: str
    creation_time: Optional[str] = None
    event_id: Optional[GWFlowEventID] = None
    files: List[GWFlowFile] = field(default_factory=list)
    bilby_jobs: List[GWFlowLinkedBilbyJob] = field(default_factory=list)

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
