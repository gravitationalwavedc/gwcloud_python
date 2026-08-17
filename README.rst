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
    >>> job = gwc.get_official_job_list()[0]
    >>> job.save_corner_plot_files()

    100%|██████████████████████████████████████| 3.76M/3.76M [00:00<00:00, 5.20MB/s]
    All 2 files saved!


GWFlow
------

To upsert a GWFlow job record and upload its pending files::

    from gwcloud_python import GWCloud

    gwc = GWCloud(api_token="<your-token>", endpoint="<endpoint>")

    # Upsert a job (idempotent — creates or updates by sname)
    result = gwc.upsert_gwflow_job(
        sname="S230101a",
        metadata={"key": "value"},
        files=[{"path": "/frames/H1.gwf", "file_name": "H1.gwf", "analysis_uid": "uid-001"}],
    )

    # Upload each pending file
    for pending_file in result.files_pending:
        gwc.upload_gwflow_file(pending_file.id, f"/local/path/{pending_file.file_name}")

To list GWFlow jobs, fetch a job by its super-name, and download one of its files::

    from gwcloud_python import GWCloud

    gwc = GWCloud(api_token="<your-token>", endpoint="<endpoint>")

    jobs = gwc.get_gwflow_job_list(search="S230101a", time_range="all", include_pruned=False)
    job = gwc.get_gwflow_job(sname="S230101a")
    if job is not None and job.files:
        gwc.download_gwflow_file(job.files[0].download_token, "/local/path/file.h5")
