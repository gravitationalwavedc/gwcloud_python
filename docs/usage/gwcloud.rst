Using the GWCloud class
=======================

The GWCloud class will be used to handle all requests to the GWCloud server.
The public methods of the GWCloud class are focused on searching for and obtaining information for specific Bilby jobs.
Below we will walk through some of the more common use cases.

Instantiating
-------------

As discussed in the previous section, we must first instantiate the class with our API token, to authenticate with the GWCloud service:

::

    from gwcloud_python import GWCloud

    gwc = GWCloud(token='my_unique_gwcloud_api_token')

If you wish to use GWCloud as an anonymous user, omit the token parameter:

::

    from gwcloud_python import GWCloud

    gwc = GWCloud()

.. warning::
    Keep in mind that anonymous access will only provide a read-only interface to publicly accessible data. You will not be able to submit new jobs or access proprietary or embargoed data.


Obtaining the official jobs
----------------------------

There is a list of several jobs labelled as "Official" jobs, which should be used as the default jobs to use for analysis of a GW event.
We are able to obtain information on the list of official Bilby jobs by running:

::

    jobs = gwc.get_official_job_list()

This method returns a list of BilbyJob instances, such as those shown below, each containing the information of the job in the GWCloud job database:

::

    >>> for job in jobs:
    ...     print(job)

    BilbyJob(name=GW150914, job_id=QmlsYnlKb2JOb2RlOjIxMQ==)
    BilbyJob(name=GW151012, job_id=QmlsYnlKb2JOb2RlOjIxMg==)
    BilbyJob(name=GW170104, job_id=QmlsYnlKb2JOb2RlOjIxMw==)
    ...

We are able to use these BilbyJob class instances to interact with the results of these jobs.

Searching the public job list
-----------------------------

While the official job list is often a good starting place to search for a desired job sample, there is often a need to search for other jobs available to the public.
To this end, the GWCloud class has another method, :meth:`~gwcloud_python.gwcloud.GWCloud.get_public_job_list`.
We are able to use this method to search the public jobs. For example, if we wish to find the jobs submitted by Thomas Reichardt at any time in the past, we can run:

::

    from gwcloud_python import TimeRange
    jobs = gwc.get_public_job_list(search="Thomas Reichardt", time_range=TimeRange.ANY)

The fields in this method operate exactly the same as on the website. We recommend using the :class:`.TimeRange` enum class to set the `time_range` field, though strings are still accepted.

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