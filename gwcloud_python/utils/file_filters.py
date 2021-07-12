from . import identifiers


def _split_file_list(identifier, file_list):
    matches = []
    others = []
    for f in file_list:
        if identifier(f.path):
            matches.append(f)
        else:
            others.append(f)
    return matches, others


def _filter_file_list(identifier, file_list):
    return [f for f in file_list if identifier(f.path)]


def default_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any HTML file
    - Any file ending with '_config_complete.ini'
    - Any PNG files in the 'data' directory
    - Any PNG files in the 'result' directory
    - Any file in the 'result' directory ending in '_merge_result.json', or '_result.json' if there is no merged file

    Parameters
    ----------
    file_list : list
        A list of dicts, each of which must have a 'path' key,
        with the value being the file path within the job files directory

    Returns
    -------
    list
        Subset of file_list containing only the paths that match the above default file criteria
    """
    # Get png files in data dir
    data_png_file_list, file_list = _split_file_list(identifiers.data_png_file, file_list)

    # Get png files in result dir
    result_png_file_list, file_list = _split_file_list(identifiers.result_png_file, file_list)

    # Get complete config file
    config_file_list, file_list = _split_file_list(identifiers.config_file, file_list)

    # Get index html file
    html_file_list, file_list = _split_file_list(identifiers.html_file, file_list)

    # Get merged json file in result dir
    result_json_file_list, file_list = _split_file_list(identifiers.result_merged_json_file, file_list)

    # If merged json doesn't exist, get result json file in result dir
    if not result_json_file_list:
        result_json_file_list, file_list = _split_file_list(identifiers.result_json_file, file_list)

    return data_png_file_list + result_png_file_list + config_file_list + html_file_list + result_json_file_list


def config_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any file ending with '_config_complete.ini'

    Parameters
    ----------
    file_list : list
        A list of dicts, each of which must have a 'path' key,
        with the value being the file path within the job files directory

    Returns
    -------
    list
        Subset of file_list containing only the paths that match the above config file criteria
    """
    return _filter_file_list(identifiers.config_file, file_list)


def png_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any PNG file

    Parameters
    ----------
    file_list : list
        A list of dicts, each of which must have a 'path' key,
        with the value being the file path within the job files directory

    Returns
    -------
    list
        Subset of file_list containing only the paths that match the above png file criteria
    """
    return _filter_file_list(identifiers.png_file, file_list)


def corner_plot_filter(file_list):
    """Takes an input file list and returns a subset of that file list containing:

    - Any file ending in '_corner.png'

    Parameters
    ----------
    file_list : list
        A list of dicts, each of which must have a 'path' key,
        with the value being the file path within the job files directory

    Returns
    -------
    list
        Subset of file_list containing only the paths that match the above corner plot file criteria
    """
    return _filter_file_list(identifiers.corner_plot_file, file_list)


def sort_file_list(file_list):
    """Sorts a file list based on the 'path' key of the dicts. Primarily used for equality checks.

    Parameters
    ----------
    file_list : list
        A list of dicts, each of which must have a 'path' key,
        with the value being the file path within the job files directory

    Returns
    -------
    list
        List containing the same members as file_list, sorted by the 'path' key of the dicts
    """
    return sorted(file_list, key=lambda f: f.path)
