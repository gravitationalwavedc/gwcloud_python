from dataclasses import dataclass


@dataclass
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
    id: str
    analysis_uid: str
    path: str
    file_name: str
    file_size: int
    uploaded: bool
    download_token: str

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
