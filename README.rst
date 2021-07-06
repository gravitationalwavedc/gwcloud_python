GWCloud Python API
==================

GWCloud is a service used to handle both the submission of `Bilby <https://pypi.org/project/bilby/>`_ jobs to a supercomputer queue and the obtaining of the results produced by these jobs.
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

    File 1 of 2 downloaded! Filesize: 1862910
    File 2 of 2 downloaded! Filesize: 1894329
    File 1 of 2 saved : result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_extrinsic_corner.png
    File 2 of 2 saved : result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_intrinsic_corner.png