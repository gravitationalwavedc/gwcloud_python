from gwdc_python.files.identifiers import match_file_suffix, match_file_base_dir, match_file_end


def html_file(file_path):
    """Checks to see if the given file path points to a HTML file

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to a HTML file, False otherwise
    """
    return match_file_suffix(file_path, 'html')


def png_file(file_path):
    """Checks to see if the given file path ends points to a PNG file

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to a PNG file, False otherwise
    """
    return match_file_suffix(file_path, 'png')


def data_dir(file_path):
    """Checks to see if the given file path starts with 'data' directory

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path starts with 'data' directory, False otherwise
    """
    return match_file_base_dir(file_path, 'data')


def result_dir(file_path):
    """Checks to see if the given file path starts with 'result' directory

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path starts with 'result' directory, False otherwise
    """
    return match_file_base_dir(file_path, 'result')


def config_file(file_path):
    """Checks to see if the given file path points towards the config file

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to config file, False otherwise
    """
    return match_file_end(file_path, '_config_complete.ini')


def merged_json_file(file_path):
    """Checks to see if the given file path points towards a merged JSON file

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to merged JSON file, False otherwise
    """
    return match_file_end(file_path, '_merge_result.json')


def unmerged_json_file(file_path):
    """Checks to see if the given file path points towards the JSON file if not run in parallel

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to JSON file, False otherwise
    """
    return match_file_end(file_path, '_result.json')


def corner_plot_file(file_path):
    """Checks to see if the given file path points towards a corner plot file

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to corner plot file, False otherwise
    """
    return match_file_end(file_path, '_corner.png')


def data_png_file(file_path):
    """Checks to see if the given file path points to a PNG file in the 'data' directory

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to PNG file in 'data' directory, False otherwise
    """
    return (data_dir(file_path) and png_file(file_path))


def result_png_file(file_path):
    """Checks to see if the given file path points to a PNG file in the 'result' directory

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to PNG file in 'result' directory, False otherwise
    """
    return (result_dir(file_path) and png_file(file_path))


def result_merged_json_file(file_path):
    """Checks to see if the given file path points to a merged JSON file in the 'result' directory.

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to the desired JSON file in 'result' directory, False otherwise
    """
    return (result_dir(file_path) and merged_json_file(file_path))


def result_json_file(file_path):
    """Checks to see if the given file path points to a result JSON file in the 'result' directory.

    Parameters
    ----------
    file_path : ~pathlib.Path
        File path to check

    Returns
    -------
    bool
        True if path points to the desired JSON file in 'result' directory, False otherwise
    """
    return (result_dir(file_path) and unmerged_json_file(file_path))
