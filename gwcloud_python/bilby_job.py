from dataclasses import dataclass
import logging
from .utils import identifiers, write_file_at_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


@dataclass(init=False)
class BilbyJob:
    """
    BilbyJob class is useful for interacting with the Bilby jobs returned from a call to the GWCloud API.
    It is primarily used to store job information and obtain files related to the job.

    Parameters
    ----------
    client : GWCloud
        A reference to the GWCloud object instance from which the BilbyJob was created
    job_id : str
        The id of the Bilby job, required to obtain the files associated with it
    name : str
        Job name
    description : str
        Job description
    kwargs : dict, optional
        Extra arguments, stored in `other` attribute
    """
    client: object
    job_id: str
    name: str
    description: str
    other: dict  #: Used to retain reference to other arbitrary information returned from the GWCloud query

    def __init__(self, client, job_id, name, description, **kwargs):
        self.client = client
        self.job_id = job_id
        self.name = name
        self.description = description
        self.other = kwargs

    def _get_files_from_file_list(self, file_list):
        file_ids, file_paths = [], []

        for f in file_list:
            file_ids.append(f['downloadId'])
            file_paths.append(f['path'])

        files = self.get_files_by_id(file_ids)

        return list(zip(file_paths, files))

    def _save_files(self, root_path, files, preserve_directory_structure):
        for i, (file_path, file_contents) in enumerate(files):
            write_file_at_path(root_path, file_path, file_contents, preserve_directory_structure)
            logger.info(f'File {i+1} of {len(files)} saved : {file_path}')

        return 'Files saved!'

    def _get_file_list_subset(self, identifier):
        file_list = self.get_full_file_list()
        return [f for f in file_list if identifier(f['path'])]

    def get_full_file_list(self):
        """Get information for all files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
        """
        return self.client._get_files_by_job_id(self.job_id)

    def get_file_by_id(self, file_id):
        """Get the contents of a file

        Parameters
        ----------
        file_id : str
            Download id for the desired file

        Returns
        -------
        bytes
            Content of the file
        """
        return self.client._get_file_by_id(file_id)

    def get_files_by_id(self, file_ids):
        """Get the contents of files

        Parameters
        ----------
        file_ids : list
            List of download ids

        Returns
        -------
        list
            Contents of the files
        """
        return self.client._get_files_by_id(file_ids)

    def get_default_file_list(self):
        """Get information for the default files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
        """
        return self._get_file_list_subset(identifiers.default_file)

    def get_config_file_list(self):
        """Get information for the config files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
        """
        return self._get_file_list_subset(identifiers.config_file)

    def get_png_file_list(self):
        """Get information for the PNG files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
        """
        return self._get_file_list_subset(identifiers.png_file)

    def get_corner_plot_file_list(self):
        """Get information for the PNG files associated with this job

        Returns
        -------
        list
            List of dicts containing information on the files
        """
        return self._get_file_list_subset(identifiers.corner_plot_file)

    def get_default_files(self):
        """Obtain the content of all the default files

        Returns
        -------
        list
            List containing tuples of the file path and associated file contents
        """
        file_list = self.get_default_file_list()
        return self._get_files_from_file_list(file_list)

    def save_default_files(self, root_path, preserve_directory_structure=True):
        """Save the default files

        Parameters
        ----------
        root_path : str or pathlib.Path
            The base directory
        preserve_directory_structure : bool, optional
            Save the files in the same structure that they were downloaded in, by default True
        """
        files = self.get_default_files()
        self._save_files(root_path, files, preserve_directory_structure)

    def get_config_files(self):
        """Obtain the content of all the config files

        Returns
        -------
        list
            List containing tuples of the file path and associated file contents
        """
        file_list = self.get_config_file_list()
        return self._get_files_from_file_list(file_list)

    def save_config_files(self, root_path, preserve_directory_structure=True):
        """Save the config files

        Parameters
        ----------
        root_path : str or pathlib.PPath
            The base directory
        preserve_directory_structure : bool, optional
            Save the files in the same structure that they were downloaded in, by default True
        """
        files = self.get_config_files()
        self._save_files(root_path, files, preserve_directory_structure)

    def get_png_files(self):
        """Obtain the content of all the PNG files

        Returns
        -------
        list
            List containing tuples of the file path and associated file contents
        """
        file_list = self.get_png_file_list()
        return self._get_files_from_file_list(file_list)

    def save_png_files(self, root_path, preserve_directory_structure=True):
        """Save the PNG files

        Parameters
        ----------
        root_path : str or pathlib.Path
            The base directory
        preserve_directory_structure : bool, optional
            Save the files in the same structure that they were downloaded in, by default True
        """
        files = self.get_png_files()
        self._save_files(root_path, files, preserve_directory_structure)

    def get_corner_plot_files(self):
        """Obtain the content of all the corner plot files

        Returns
        -------
        list
            List containing tuples of the file path and associated file contents
        """
        file_list = self.get_corner_plot_file_list()
        return self._get_files_from_file_list(file_list)

    def save_corner_plot_files(self, root_path, preserve_directory_structure=True):
        """Save the corner plot files

        Parameters
        ----------
        root_path : str or pathlib.Path
            The base directory
        preserve_directory_structure : bool, optional
            Save the files in the same structure that they were downloaded in, by default True
        """
        files = self.get_corner_plot_files()
        self._save_files(root_path, files, preserve_directory_structure)
