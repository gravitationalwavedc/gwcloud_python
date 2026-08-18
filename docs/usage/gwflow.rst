Working with GWFlow
===================

GWFlow is a service within GWCloud for tracking analyses and the files associated with them.
While the rest of this package focuses on submitting and obtaining Bilby jobs, the GWFlow methods let you register your own analyses, mirror their files into GWCloud, and link them to the Bilby jobs that produced them.
You might use these methods when you are running analyses outside of the standard Bilby workflow but still want to keep track of the analyses, and their results, in GWCloud.

Registering and uploading files
-------------------------------

The first step is to register an analysis with GWFlow.
The :meth:`~gwcloud_python.gwcloud.GWCloud.upsert_gwflow_job` method creates a new GWFlow job record, or updates an existing one, keyed by its super-name (``sname``).
Because the operation is transactional and idempotent, you can call it as many times as you like with the same ``sname`` without creating duplicate records:

::

    result = gwc.upsert_gwflow_job(
        sname="S230101a",
        metadata={"detector": "H1"},
        files=[{"path": "/frames/H1.gwf", "file_name": "H1.gwf", "analysis_uid": "uid-001"}],
    )

The result contains the details of the job, along with a list of any files that are still pending mirroring.

Once a job has been registered, we can see which of its files have not yet been mirrored into GWCloud using :meth:`~gwcloud_python.gwcloud.GWCloud.get_gwflow_pending_files`:

::

    pending_files = gwc.get_gwflow_pending_files()

This returns a list of :class:`~gwcloud_python.gwflow_pending_file.GWFlowPendingFile` instances, one for each file that still needs to be uploaded.

We can then upload the pending files to GWCloud using :meth:`~gwcloud_python.gwcloud.GWCloud.upload_gwflow_file`, passing the file ID from the pending file list along with the local path to the file:

::

    for pending_file in pending_files:
        gwc.upload_gwflow_file(pending_file.id, f"/local/path/{pending_file.file_name}")

The method returns the size of the uploaded file.

Linking Bilby jobs
------------------

If a GWFlow analysis is associated with a Bilby job, we can link the two together using :meth:`~gwcloud_python.gwcloud.GWCloud.link_bilby_job_to_gwflow`.
This takes the ID of the Bilby job, the super-name of the GWFlow job, and a unique identifier for the analysis:

::

    gwc.link_bilby_job_to_gwflow(job_id=job.job_id, sname="S230101a", analysis_uid="uid-001")

Passing an empty string for the ``sname`` will unlink the Bilby job from its current GWFlow analysis.

Finding and downloading results
-------------------------------

To find the GWFlow jobs we have registered, we can use :meth:`~gwcloud_python.gwcloud.GWCloud.get_gwflow_job_list` to obtain a list of all jobs, optionally filtered by search terms, time range, and whether pruned jobs are included:

::

    jobs = gwc.get_gwflow_job_list(search="S230101a", time_range="all", include_pruned=False)

If we know the super-name of a particular job, we can obtain that single job directly with :meth:`~gwcloud_python.gwcloud.GWCloud.get_gwflow_job`:

::

    job = gwc.get_gwflow_job(sname="S230101a")

This returns a :class:`~gwcloud_python.gwflow_job.GWFlowJob` instance, or ``None`` if no such job exists.
The instance includes the files associated with the job, each with a download token.

Finally, we can download a file to our local machine using :meth:`~gwcloud_python.gwcloud.GWCloud.download_gwflow_file`, passing the file's download token and the local path where we would like to save it:

::

    gwc.download_gwflow_file(job.files[0].download_token, "results/S230101a/file.h5")
