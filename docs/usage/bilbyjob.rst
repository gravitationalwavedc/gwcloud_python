Using the BilbyJob class
========================

Obtaining job files
-------------------

Once we have a reference to our job, we are able to use any of it's methods to help with obtaining the results. For example, we can see the default list of files by running:

::

    job.get_default_file_list()

which returns a list of all the default files available for download. To actually download and save these files, we can use:

::

    job.save_default_files('directory/to/store/files')

There are numerous other methods, each with the same naming conventions, that can be used to select different sets of result files.
For example, :meth:`~gwcloud_python.bilby_job.BilbyJob.get_png_file_list` and :meth:`~gwcloud_python.bilby_job.BilbyJob.save_png_files` can be used to look at and obtain a list of all the PNG files in the job results.