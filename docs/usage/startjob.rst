Starting a job
==============

The gwcloud-python API can also be used to start a Bilby job, as we can using the Bilby user interface.
However, instead of filling out a form of all the job parameters, we need a Bilby .ini file, along with a job name, description and privacy setting.
For convenience, .ini files can be downloaded from existing jobs using :meth:`~.BilbyJob.get_config_files` or :meth:`~.BilbyJob.save_config_files`.
Check the example :ref:`here <get-file-label>`.

Using a Bilby .ini file
-----------------------

We can submit a job just by providing a path to the .ini file on our local machine, for example:

::

    job = gwc.start_bilby_job_from_file(
        job_name="a_meaningful_name",
        job_description="This job will usher in a new age of learning",
        private=True,
        ini_file="path/to/file.ini"
    )

This method, and the one below, return a BilbyJob instance containing information on your new job.
You should be able to :ref:`monitor the progress <status-label>` of your job through the API or through the web interface.

Using the contents of a Bilby .ini file
---------------------------------------

Instead of passing in a path to an .ini file, we are also able to pass in the contents of the file as a string:

::

    job = gwc.start_bilby_job_from_string(
        job_name="another_meaningful_name",
        job_description="This job will bring world peace",
        private=True,
        ini_string=contents_of_ini_file
    )

This could be used to programmatically modify the contents of an .ini file (in a loop, for example) and submit a new job.