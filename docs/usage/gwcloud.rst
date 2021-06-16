Using the GWCloud class
=======================

Obtaining the preferred jobs
----------------------------

Here, the GWCloud class will be used to handle all requests. For example, we are able to obtain information on the list of "preferred" Bilby jobs by running

::

    jobs = gwc.get_preferred_job_list()

which will return a list of jobs like this

::

    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxMQ==', name='GW150914', description='Results for gravitational wave event GW150914', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxMg==', name='GW151012', description='Results for gravitational wave event GW151012', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxMw==', name='GW170104', description='Results for gravitational wave event GW170104', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxNA==', name='GW170729', description='Results for gravitational wave event GW170729', other={'user': 'Paul Lasky'})
    BilbyJob(job_id='QmlsYnlKb2JOb2RlOjIxNQ==', name='GW170823', description='Results for gravitational wave event GW170823', other={'user': 'Paul Lasky'})

We are able to use these BilbyJob class instances to interface the results of these jobs. Let's grab the job for GW150914!

Obtaining a specific job
------------------------

Given that we already have the list of jobs here, we can get the job from the list:

::

    job = jobs[0] # Index of the GW150914 job

However, if we didn't have access to this list, we can obtain a job ID and obtain the data for this job by using the GWCloud instance:

::

    job = gwc.get_job_by_id('QmlsYnlKb2JOb2RlOjIxMQ==')

Both of these methods for getting a job yield equivalent results, but may be used in different ways.