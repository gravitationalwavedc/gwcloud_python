import logging
from .utils import file_lists, write_file_at_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class BilbyJob:
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
    job_status : dict
        Status of job, should have 'name' and 'date' keys corresponding to the status code and when it was produced
    kwargs : dict, optional
        Extra arguments, stored in `other` attribute
    """

    DEFAULT_FILE_LIST_FILTERS = {
        'default': file_lists.default_filter,
        'config': file_lists.config_filter,
        'png': file_lists.png_filter,
        'corner_plot': file_lists.corner_plot_filter,
    }

    def __init__(self, client, job_id, name, description, job_status, **kwargs):
        self.client = client
        self.job_id = job_id
        self.name = name
        self.description = description
        self.status = job_status
        self.other = kwargs

    def __repr__(self):
        return f"BilbyJob(name={self.name}, job_id={self.job_id})"

    def get_full_file_list(self):
        """Get information for all files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
        """
        return self.client._get_files_by_job_id(self.job_id)

    def get_file_by_token(self, file_token):
        """Get the contents of a file

        Parameters
        ----------
        file_token : str
            Download token for the desired file

        Returns
        -------
        bytes
            Content of the file
        """
        return self.client._get_file_by_id(
            self.client._get_download_id_from_token(self.job_id, file_token)
        )

    def get_files_by_tokens(self, file_tokens):
        """Get the contents of files

        Parameters
        ----------
        file_tokens : list
            List of download tokens

        Returns
        -------
        list
            Contents of the files
        """
        return self.client._get_files_by_id(
            self.client._get_download_ids_from_tokens(self.job_id, file_tokens)
        )

    @classmethod
    def register_file_list_filter(cls, name, file_list_filter_fn):
        """Register a function used to filter the file list.
        This will create three methods on the class using this filter function:

        - get_{name}_file_list
        - get_{name}_files
        - save_{name}_files

        where {name} is the input name string.

        Parameters
        ----------
        name : str
            String used to name the added methods
        file_list_filter_fn : function
            A function that takes in the full file list and returns only the desired entries from the list
        """
        _register_file_list_filter(name, file_list_filter_fn)
        cls.DEFAULT_FILE_LIST_FILTERS['name'] = file_list_filter_fn


def _register_file_list_filter(name, file_list_filter_fn):
    spaced_name = name.replace('_', ' ')

    def _get_file_list_subset(self):
        return file_list_filter_fn(
            self.get_full_file_list()
        )

    file_list_fn_name = f'get_{name}_file_list'
    file_list_fn = _get_file_list_subset
    file_list_fn.__doc__ = f"""Get information for the {spaced_name} files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
    """
    setattr(BilbyJob, file_list_fn_name, file_list_fn)

    def _get_files_from_file_list(self):
        file_list = _get_file_list_subset(self)
        file_tokens, file_paths = [], []

        for f in file_list:
            file_tokens.append(f['downloadToken'])
            file_paths.append(f['path'])

        files = self.get_files_by_tokens(file_tokens)

        return list(zip(file_paths, files))

    files_fn_name = f'get_{name}_files'
    files_fn = _get_files_from_file_list
    files_fn.__doc__ = f"""Obtain the content of all the {spaced_name} files

        Returns
        -------
        list
            List containing tuples of the file path and associated file contents
    """
    setattr(BilbyJob, files_fn_name, files_fn)

    def _save_files(self, root_path, preserve_directory_structure=True):
        files = _get_files_from_file_list(self)
        for i, (file_path, file_contents) in enumerate(files):
            write_file_at_path(root_path, file_path, file_contents, preserve_directory_structure)
            logger.info(f'File {i+1} of {len(files)} saved : {file_path}')

        return 'Files saved!'

    save_fn_name = f'save_{name}_files'
    save_fn = _save_files
    save_fn.__doc__ = f"""Save the {spaced_name} files

        Parameters
        ----------
        root_path : str or pathlib.Path
            The base directory into which the files will be saved
        preserve_directory_structure : bool, optional
            Save the files in the same structure that they were downloaded in, by default True
    """
    setattr(BilbyJob, save_fn_name, save_fn)


for name, file_filter in BilbyJob.DEFAULT_FILE_LIST_FILTERS.items():
    _register_file_list_filter(name, file_filter)
