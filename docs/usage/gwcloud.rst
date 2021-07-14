Using the GWCloud class
=======================

The GWCloud class will be used to handle all requests to the GWCloud server.
The public methods of the GWCloud class are focused on searching for and obtaining information for specific Bilby jobs.
Below we will walk through some of the more common use cases.

Obtaining the preferred jobs
----------------------------

There is a list of several jobs labelled as "Preferred" jobs, which should be used as the default jobs to use for analysis of a GW event.
We are able to obtain information on the list of preferred Bilby jobs by running:

::

    jobs = gwc.get_preferred_job_list()

This method returns a list of BilbyJob instances, each containing the information of the job in the GWCloud job database:

::

    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxMQ==', name='GW150914', description='Results for gravitational wave event GW150914', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxMg==', name='GW151012', description='Results for gravitational wave event GW151012', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxMw==', name='GW170104', description='Results for gravitational wave event GW170104', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxNA==', name='GW170729', description='Results for gravitational wave event GW170729', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxNQ==', name='GW170823', description='Results for gravitational wave event GW170823', other={'user': 'Paul Lasky'})

We are able to use these BilbyJob class instances to interact with the results of these jobs.

Searching the public job list
-----------------------------

While the preferred job list is often a good starting place to search for a desired job sample, there is often a need to search for other jobs available to the public.
To this end, the GWCloud class has another method, :meth:`~gwcloud_python.gwcloud.GWCloud.get_public_job_list`.
We are able to use this method to search the public jobs. For example, if we wish to find the jobs submitted by Thomas Reichardt at any time in the past, we can run:

::

    from gwcloud_python import TimeRange
    jobs = gwc.get_public_job_list(search="Thomas Reichardt", time_range=TimeRange.ANY)

The fields in this method operate exactly the same as on the website. We recommend using the :class:`~gwcloud_python.gwcloud.TimeRange` enum class to set the `time_range` field, though strings are still accepted.

For the sake of clarity, the :meth:`~gwcloud_python.gwcloud.GWCloud.get_preferred_job_list` method is effectively shorthand for performing a search on the public job list with the search terms "preferred lasky" with the time range set to "Any time".


Obtaining a single specific job
-------------------------------

If we have a list of BilbyJob instances, as above, we are able to use the list index to reference a specific job from that list.
For example, if we want to work with the GW150914 job, we can just grab the first job in the list:

::

    job = jobs[0] # Index of the GW150914 job

However, we are also able to obtain single jobs from the database if we know their job ID, using the :meth:`~gwcloud_python.gwcloud.GWCloud.get_job_by_id` method:

::

    job = gwc.get_job_by_id('QmlsYnlKb2JOb2RlOjIxMQ==')

Both of these methods for getting a job yield equivalent results, but may be used in different ways.