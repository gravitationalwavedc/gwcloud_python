from gwdc_python.files.filters import filter_file_list
from . import identifiers


def default_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any HTML file
    - Any file ending with '_config_complete.ini'
    - Any PNG files in the 'data' directory
    - Any PNG files in the 'result' directory
    - Any file in the 'result' directory ending in '_merge_result.json', or '_result.json' if there is no merged file

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    .FileReferenceList
        Subset of the input FileReferenceList containing only the paths that match the above default file criteria
    """
    # Get png files in data dir
    data_png_file_list, file_list = filter_file_list(identifiers.data_png_file, file_list)

    # Get png files in result dir
    result_png_file_list, file_list = filter_file_list(identifiers.result_png_file, file_list)

    # Get complete config file
    config_file_list, file_list = filter_file_list(identifiers.config_file, file_list)

    # Get index html file
    html_file_list, file_list = filter_file_list(identifiers.html_file, file_list)

    # Get merged json file in result dir
    result_json_file_list, file_list = filter_file_list(identifiers.result_merged_json_file, file_list)

    # If merged json doesn't exist, get result json file in result dir
    if not result_json_file_list:
        result_json_file_list, file_list = filter_file_list(identifiers.result_json_file, file_list)

    return data_png_file_list + result_png_file_list + config_file_list + html_file_list + result_json_file_list


def config_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any file ending with '_config_complete.ini'

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    .FileReferenceList
        Subset of the input FileReferenceList containing only the paths that match the above config file criteria
    """
    return filter_file_list(identifiers.config_file, file_list)[0]


def png_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any PNG file

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    .FileReferenceList
        Subset of the input FileReferenceList containing only the paths that match the above png file criteria
    """
    return filter_file_list(identifiers.png_file, file_list)[0]


def corner_plot_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any file ending in '_corner.png'

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    .FileReferenceList
        Subset of the input FileReferenceList containing only the paths that match the above corner plot file criteria
    """
    return filter_file_list(identifiers.corner_plot_file, file_list)[0]


def result_json_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any file in the 'result' directory ending in '_merge_result.json'
    - Or, any file in the 'result' directory ending in '_result.json'

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    .FileReferenceList
        Subset of the input FileReferenceList containing only the paths that match the merged json file criteria
    """
    # Get merged json file in result dir
    result_json_file_list, _ = filter_file_list(identifiers.result_merged_json_file, file_list)

    # If merged json doesn't exist, get result json file in result dir
    if not result_json_file_list:
        result_json_file_list, _ = filter_file_list(identifiers.result_json_file, file_list)

    return result_json_file_list


def sort_file_list(file_list):
    """Sorts a file list based on the 'path' key of the dicts. Primarily used for equality checks.

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    .FileReferenceList
        A FileReferenceList containing the same members as the input,
        sorted by the path attribute of the FileReference objects
    """
    return sorted(file_list, key=lambda f: f.path)
