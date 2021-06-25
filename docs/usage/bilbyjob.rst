Using the BilbyJob class
========================

A completed Bilby job will have a list of files associated with it.
With an instance of the BilbyJob class, we are able to obtain the result files stored in the database.

Obtaining a job file list
-------------------------

If we want to examine which files are associated with a Bilby job, we can obtain a list of file paths, sizes and download tokens as follows:

::

    files = job.get_full_file_list()

This will return a list of dictionaries containing the information for all files associated with the job:

::

    {'path': PosixPath('GW150914_config_complete.ini'), 'fileSize': '5167', 'downloadToken': 'e7908b80-f3bc-4727-b273-23fb90111430'}
    {'path': PosixPath('archive.tar.gz'), 'fileSize': '3446179840', 'downloadToken': '268601c8-57f6-47b5-8521-96c406145a56'}
    {'path': PosixPath('GW150914.ini'), 'fileSize': '4851', 'downloadToken': 'ab8d8302-82d2-48bc-a23b-16c72b9cf4ab'}
    {'path': PosixPath('results_page/overview.html'), 'fileSize': '20803', 'downloadToken': '2c9621c9-1b0e-4c03-8962-529ee23cd3ea'}
    ...
    {'path': PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_1d/recalib_L1_phase_1_cdf.png'), 'fileSize': '73316', 'downloadToken': '49bb60e3-08fe-44f1-bfea-c5761fa38c8c'}
    {'path': PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_1d/recalib_L1_phase_5_cdf.png'), 'fileSize': '75111', 'downloadToken': '1d83b9e3-6024-414d-8857-c492faa6b0b0'}
    {'path': PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_1d/recalib_L1_amplitude_2_cdf.png'), 'fileSize': '74434', 'downloadToken': '2f8b9feb-bac1-4c54-bc46-e4a111be6293'}

Obtaining the full file list is rarely required, hence there are several methods by which to obtain sensible portions of the file list for you.
For example, to obtain just the default file list, which are the result files of primary interest, we can use the method :meth:`~gwcloud_python.bilby_job.BilbyJob.get_default_file_list`.
There are numerous other methods, each with the same naming conventions, that can be used to select different sets of result files.
To obtain just the list of PNG files, we can use :meth:`~gwcloud_python.bilby_job.BilbyJob.get_png_file_list`. This is applicable to the methods displayed below, too.

Obtaining job file data
-----------------------

There are a couple of ways that we are able to actually obtain the data from the job files.
If we have a list of files already, we can extract the download tokens and then use the :meth:`~gwcloud_python.bilby_job.BilbyJob.get_files_by_tokens` method.
Typically, however, the best way to obtain job files is to use one of the methods such as :meth:`~gwcloud_python.bilby_job.BilbyJob.get_default_files`:

::

    file_data = job.get_default_files()

which returns a list of all the contents of the default files available for download.

Saving job files
----------------

It is often useful to download the files instead of manipulating them in a program.
Another set of methods, such as :meth:`~gwcloud_python.bilby_job.BilbyJob.save_default_files`, has been provided to download and save a subset of the results files.
For example, we can save all the default files, keeping the directory structure intact, by running:

::

    job.save_default_files('directory/to/store/files')

