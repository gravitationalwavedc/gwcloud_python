from .utils import file_filters
from .event_id import EventID

from gwdc_python.jobs import JobBase
from gwdc_python.logger import create_logger

logger = create_logger(__name__)


class BilbyJob(JobBase):
    """
    BilbyJob class is useful for interacting with the Bilby jobs returned from a call to the GWCloud API.
    It is primarily used to store job information and obtain files related to the job.

    Parameters
    ----------
    client : ~gwcloud_python.gwcloud.GWCloud
        A reference to the GWCloud object instance from which the BilbyJob was created
    job_id : str
        The id of the Bilby job, required to obtain the files associated with it
    name : str
        Job name
    description : str
        Job description
    user : str
        User that ran the job
    event_id : dict
        Event ID associated with job, should have keys corresponding to an
        :class:`~.EventID` object
    job_status : dict
        Status of job, should have 'name' and 'date' keys corresponding to the status code and when it was produced
    kwargs : dict, optional
        Extra arguments, stored in `other` attribute
    """

    FILE_LIST_FILTERS = {
        'default': file_filters.default_filter,
        'config': file_filters.config_filter,
        'png': file_filters.png_filter,
        'corner_plot': file_filters.corner_plot_filter,
        'result_json': file_filters.result_json_filter
    }

    def __init__(self, client, job_id, name, description, user, event_id, job_status, **kwargs):
        super().__init__(client, job_id, name, description, user, job_status)
        self.event_id = EventID(**event_id) if event_id else None
        self.other = kwargs

    def _update_job(self, **kwargs):
        query = """
            mutation BilbyJobEventIDMutation($input: UpdateBilbyJobMutationInput!) {
                updateBilbyJob(input: $input) {
                    result
                }
            }
        """

        variables = {
            "input": {
                "job_id": self.job_id,
                **kwargs
            }
        }

        return self.client.request(query=query, variables=variables)

    def set_name(self, name):
        """Set the name of a Bilby Job

        Parameters
        ----------
        event_id : str
            The new name
        """

        data = self._update_job(name=str(name))
        self.name = name
        logger.info(data['update_bilby_job']['result'])

    def set_description(self, description):
        """Set the description of a Bilby Job

        Parameters
        ----------
        event_id : str
            The new description
        """

        data = self._update_job(description=str(description))
        self.description = description
        logger.info(data['update_bilby_job']['result'])

    def set_event_id(self, event_id=None):
        """Set the Event ID of a Bilby Job

        Parameters
        ----------
        event_id : EventID or str, optional
            The desired Event ID, by default None
        """

        if isinstance(event_id, EventID):
            new_event_id = event_id.event_id
        elif isinstance(event_id, str):
            new_event_id = event_id
        elif event_id is None:
            new_event_id = ''
        else:
            raise Exception('Parameter event_id must be an EventID, a string or None')

        data = self._update_job(event_id=new_event_id)
        self.event_id = self.client.get_event_id(event_id=new_event_id)
        logger.info(data['update_bilby_job']['result'])
