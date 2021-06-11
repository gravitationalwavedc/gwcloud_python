from .gwcloud import GWCloud
from .bilby_job import BilbyJob

try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version
__version__ = version('gwcloud_python')