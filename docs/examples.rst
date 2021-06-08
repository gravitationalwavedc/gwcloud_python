Examples
========

Most scripts involving the GWCloud API will be started by using you API token to authenticate with the GWCloud service.

::

    from gwcloud_python import GWCloud

    gwc = GWCloud(token='my_unique_gwcloud_api_token')

Here, the `GWCloud` class will be used to handle all requests. For example, we are able to obtain information on the list of "preferred" Bilby jobs by running

::

    jobs = gwc.get_preferred_job_list()

Then, if we find a job we want to examine, we can save the list of files with

::

    job = jobs[0] # Arbitrary first job in list
    job.save_default_files('scripts')