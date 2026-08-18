from dataclasses import dataclass
from typing import Optional


@dataclass
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
    id: str
    sname: str
    analysis_uid: str
    path: str
    file_name: str
    md5_sum: Optional[str] = None

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
