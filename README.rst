GWCloud Python API
==================

`GWCloud <https://gwcloud.org.au/>`_ is a service used to handle both the submission of `Bilby <https://pypi.org/project/bilby/>`_ jobs to a supercomputer queue and the obtaining of the results produced by these jobs.
While there is a web interface for this service, which is recommended for beginners, this package can be used to allow Bilby job submission and manipulation from Python scripts.

Check out the `documentation <https://gwcloud-python.readthedocs.io/en/latest/>`_ for more information.

Installation
------------

The gwcloud-python package can be installed with

::

    pip install gwcloud-python


Example
-------

::

    >>> from gwcloud_python import GWCloud
    >>> gwc = GWCloud(token='<user_api_token_here>')
    >>> job = gwc.get_preferred_job_list()[0]
    >>> job.save_corner_plot_files()

    100%|██████████████████████████████████████| 3.76M/3.76M [00:00<00:00, 5.20MB/s]
    All 2 files saved!
