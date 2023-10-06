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

Submitting job to a specific cluster
------------------------------------

By default, all jobs will be sent to OzSTAR. However, we can specify which cluster the job should be sent to by using the cluster argument in the previous methods.
For example, if we wish to send our job to the Caltech cluster, we can run:

::

    from gwcloud_python import Cluster

    job = gwc.start_bilby_job_from_string(
        job_name="CIT_Job",
        job_description="OzSTAR just isn't cutting it",
        private=True,
        ini_string=contents_of_ini_file,
        cluster=Cluster.CIT
    )

The Cluster enum is provided as a utility to help avoid mistakes, though the string "cit" would still be accepted.
For the list of available clusters, we can check the :class:`.Cluster` class.

.. _status-label:

Monitoring job status
---------------------

While :class:`.BilbyJob` instances only show the job name and ID when printed, they store more useful attributes, such as the description, the job status and others.
To observe the status of a job, we can just print the :attr:`.BilbyJob.status` attribute. This attribute stores a dictionary containing the status name and the date when this status began.
For example, if we print the job status, we are shown that the job has been completed, and hence will have an associated list of result files:

::
    
    >>> print(job.status)

    {'name': 'Completed', 'date': '2021-05-31T03:16:36+00:00'}


Modifying job properties
------------------------

After a job has been submitted, we are able to still modify some of its properties in the GWCloud service.
For example, we can use the :meth:`.BilbyJob.set_name` method to change the name of the job:

::

    job.set_name(name='modified_job_name')

Likewise, we are able to change the job description and event ID using :meth:`.BilbyJob.set_description` and :meth:`.BilbyJob.set_event_id`, respectively.
