Starting a job
==============

Now that we have seen how to obtain jobs and their results, we will show you how to start a Bilby job.
For this, we need a Bilby .ini file, along with a job name, description and whether or not you want the job to be private.
We can submit a job just by providing a path to the ini file on our local machine, for example:

::

    job_id = gwc.start_bilby_job_from_file(
        job_name="a_meaningful_name",
        job_description="This job will usher in a new age of learning",
        private=True,
        ini_file="path/to/file.ini"
    )

If you already have the .ini file open, you are able to submit the contents of the file as a string, as:

::

    job_id = gwc.start_bilby_job_from_string(
        job_name="a_meaningful_name",
        job_description="This job will bring world peace",
        private=True,
        ini_string=contents_of_ini_file
    )

These methods return the ID for your job, which can be used to access the job with :meth:`~gwcloud_python.gwcloud.GWCloud.get_job_by_id`.
You should be able to monitor the progress of your job through the API or through the web interface.