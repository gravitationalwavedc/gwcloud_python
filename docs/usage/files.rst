Working with FileReferences and FileReferenceLists
==================================================

A completed Bilby job will have a list of files associated with it.
With an instance of the :class:`.BilbyJob` class, we are able to obtain the result files stored in the database.

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
To obtain just the list of PNG files, we can use :meth:`~.BilbyJob.get_png_file_list`. These naming conventions are applicable to the methods used for obtaining the job files, too.


Saving job files
----------------

There are a couple of ways that we are able to actually obtain the data from desired job files.
In general, we recommend streaming the files and saving them straight to disk. This is especially important for large files, or large numbers of files.
Hence, another set of methods, such as :meth:`~.BilbyJob.save_default_files`, has been provided to download and save a subset of the results files.
For example, we can save all the default files, keeping the directory structure intact, by running:

::

    job.save_default_files('directory/to/store/files')

which should give output for the download in the form of a progress bar:

::

    100%|██████████████████████████████████████| 1.00G/1.00G [01:40<00:00, 9.94MB/s]
    All 247 files saved!

.. _get-file-label:

Obtaining job file data
-----------------------

If we want to just obtain the contents of some files, we can also download the files and store them in memory using methods such as :meth:`~.BilbyJob.get_default_files`.
For example, if we wish to obtain the .ini file of a job so that we can programmatically modify and resubmit it, we could use :meth:`~.BilbyJob.get_config_files`:

::

    file_data = job.get_config_files()

which returns a list of all the contents of the config files available for download.

.. warning::
    We recommend only using these methods when dealing with small total file sizes, as storing many MB or GB in memory can be detrimental to the performance of your machine.


Filtering files by path
-----------------------

If none of the provided methods return the desired subset of files, the full :class:`.FileReferenceList` can be filtered by using the more custom :meth:`~.FileReferenceList.filter_list_by_path` method.
This enables us to pick only the files we want based on the directories, the file name or the file extension.
For example, if we want to find all JSON files in the 'result' directory, we can can run:

::

    files = job.get_full_file_list()
    result_json_files = files.filter_list_by_path(directory='result', extension='json')

This returns a new :class:`.FileReferenceList` with contents like:

::

    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_merge_result.json'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_par0_result.json'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_par1_result.json'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_par2_result.json'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_par3_result.json'))
    FileReference(path=PosixPath('result/GW150914_data0_1126259462-391_analysis_H1L1_dynesty_par4_result.json'))

We are able to save or obtain the files for this custom :class:`.FileReferenceList` using the :meth:`~.GWCloud.save_files_by_reference` and :meth:`~.GWCloud.get_files_by_reference` methods.
For example, to save the above :code:`result_json_files`, we run:

::

    gwc.save_files_by_reference(result_json_files, 'directory/to/store/files')

Note that a :class:`.FileReferenceList` object can contain references to files from many different Bilby Jobs.
The :meth:`~.GWCloud.save_files_by_reference` and :meth:`~.GWCloud.get_files_by_reference` methods are able to handle such cases.