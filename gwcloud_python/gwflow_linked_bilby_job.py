from dataclasses import dataclass


@dataclass
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
    id: str
    name: str
    gwflow_analysis_uid: str

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d.get('id'),
            name=d.get('name'),
            gwflow_analysis_uid=d.get('gwflowAnalysisUid') or d.get('gwflow_analysis_uid'),
        )
