from dataclasses import dataclass


@dataclass
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
    event_id: str
    trigger_id: str
    nickname: str
    gps_time: float

    @classmethod
    def from_dict(cls, d):
        return cls(
            event_id=d.get('eventId') or d.get('event_id'),
            trigger_id=d.get('triggerId') or d.get('trigger_id'),
            nickname=d.get('nickname'),
            gps_time=d.get('gpsTime') if 'gpsTime' in d else d.get('gps_time'),
        )
