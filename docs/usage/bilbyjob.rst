Using the BilbyJob class
========================

A completed Bilby job will have a list of files associated with it.
With an instance of the BilbyJob class, we are able to obtain the result files stored in the database.

Obtaining a job file list
-------------------------

If we want to examine which files are associated with a Bilby job, we can obtain a list of file paths, sizes and download tokens as follows:

::

    files = job.get_full_file_list()

This will return a :class:`.FileReferenceList`, which contains FileReference instances for all files associated with the job:

::

    FileReference(path=PosixPath('data/H1_GW150914_data0_1126259462-391_generation_frequency_domain_data.png'))
    FileReference(path=PosixPath('data/L1_GW150914_data0_1126259462-391_generation_frequency_domain_data.png'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_1d/a_1_cdf.png'))
    ...
    FileReference(path=PosixPath('GW150914_config_complete.ini'))
    FileReference(path=PosixPath('results_page/overview.html'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_result.json'))

Obtaining the full file list is rarely required, hence there are several convenient methods by which we can obtain sensible subsets of the file list instead.
For example, to obtain just the set of default files (detailed in the description of the :func:`~.file_filters.default_filter`), which are the result files of primary interest, we can use the method :meth:`~.BilbyJob.get_default_file_list`.
There are numerous other methods, each with the same naming conventions, that can be used to select different sets of result files.
To obtain just the list of PNG files, we can use :meth:`~.BilbyJob.get_png_file_list`. These naming conventions are applicable to the methods displayed below, too.

Obtaining job file data
-----------------------

There are a couple of ways that we are able to actually obtain the data from the job files.
If we have a :class:`.FileReferenceList` that already contains information on the files we want, we can use the :meth:`~.BilbyJob.get_files_by_reference` method.
Typically, however, the best way to obtain job files is to use one of the methods such as :meth:`~.BilbyJob.get_default_files`:

::

    file_data = job.get_default_files()

which returns a list of all the contents of the default files available for download.

Saving job files
----------------

For large numbers of files, or files with a large size, we recommend saving the files and reading them in as needed instead of keeping them all in memory.
Hence, another set of methods, such as :meth:`~.BilbyJob.save_default_files`, has been provided to download and save a subset of the results files.
For example, we can save all the default files, keeping the directory structure intact, by running:

::

    job.save_default_files('directory/to/store/files')
