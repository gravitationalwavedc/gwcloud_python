from .gwcloud import GWCloud
from .bilby_job import BilbyJob
from .file_reference import FileReference, FileReferenceList

try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version
__version__ = version('gwcloud_python')