from functools import partial
from pathlib import Path
import re
import requests

GWCLOUD_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/job/apiv1/file/?fileId='
GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/bilby/file_download/?fileId='


def write_file_at_path(root_path, file_path, file_contents, preserve_directory_structure=True):
    """Write a file at the given path, with the given contents

    Parameters
    ----------
    root_path : str or pathlib.Path
        The base directory
    file_path : pathlib.Path
        The file path within the base directory, including the name of the file
    file_contents : bytes
        The contents of the file
    preserve_directory_structure : bool, optional
        Create any directories present in `file_path`, by default True
    """
    if preserve_directory_structure:
        path = root_path / file_path
    else:
        path = root_path / Path(file_path.name)

    path.parents[0].mkdir(parents=True, exist_ok=True)
    path.write_bytes(file_contents)


def remove_path_anchor(path):
    """Removes the path anchor, making it a relative path

    Parameters
    ----------
    path : pathlib.Path
        Path from which to strip anchor

    Returns
    -------
    Path
        Relative path
    """
    if path.is_absolute():
        return path.relative_to(path.anchor)
    else:
        return path


def to_snake_case(key):
    """Rewrites a camelCase string in snake_case

    Parameters
    ----------
    key : str
        Key to convert

    Returns
    -------
    str
        Key in snake_case
    """
    return re.sub('([A-Z]+)', r'_\1', key).lower()


def to_camel_case(key):
    """Rewrites a snake_case string in camelCase

    Parameters
    ----------
    key : str
        Key to convert

    Returns
    -------
    str
        Key in camelCase
    """
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), key)


def _rename_key(key, key_map={}):
    return key_map.get(key, key)


def _apply_key_funcs(key, funcs):
    for func in funcs:
        key = func(key)
    return key


def recursively_map_dict_keys(obj, func):
    """Recursively traverse dicts or lists of dicts to apply a function to each dictionary key

    Parameters
    ----------
    obj : dict or list
        Object to traverse
    func : function
        Function to apply to dictionary keys

    Returns
    -------
    dict
        Dictionary with keys modified by `func`
    """
    if isinstance(obj, dict):  # if dict, apply to each key
        return {func(k): recursively_map_dict_keys(v, func) for k, v in obj.items()}
    elif isinstance(obj, list):  # if list, apply to each element
        return [recursively_map_dict_keys(elem, func) for elem in obj]
    else:
        return obj


def rename_dict_keys(input_dict, key_map):
    """Renames the keys in a dictionary

    Parameters
    ----------
    input_dict : dict
        Dictionary for which to change the keys
    key_map : dict
        Dictionary which specifies old keys to be swapped with new keys in the input_dict, e.g `{'old_key': 'new_key'}`

    Returns
    -------
    dict
        Copy of `input_dict` with old keys subbed for new keys
    """
    funcs = [partial(_rename_key, key_map=key_map)]
    return recursively_map_dict_keys(input_dict, partial(_apply_key_funcs, funcs=funcs))


def convert_dict_keys(input_dict, key_map={}, reverse=False):
    """Convert the keys of a dictionary from camelCase to snake_case

    Parameters
    ----------
    input_dict : dict
        Dictionary for which to convert the keys
    key_map : dict, optional
        Dictionary which specifies old keys to be swapped with new keys in `input_dict`,
        e.g `{'old_key': 'new_key'}`, by default {}
    reverse : bool, optional
        If True, will return snake_case keys to camelCase, by default False

    Returns
    -------
    dict
        Copy of `input_dict` with keys converted from camelCase to snake_case, and optional other key sets exchanged
    """
    funcs = []
    if key_map:
        funcs.append(partial(_rename_key, key_map=key_map))

    funcs.append(to_camel_case if reverse else to_snake_case)

    return recursively_map_dict_keys(input_dict, partial(_apply_key_funcs, funcs=funcs))


def _get_file_map_fn(file_id, file_path, progress_bar, is_uploaded_job=False):
    endpoint = GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
        if not is_uploaded_job else \
        GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT

    download_url = endpoint + str(file_id)
    content = b''
    with requests.get(download_url, stream=True) as request:
        for chunk in request.iter_content(chunk_size=1024 * 16, decode_unicode=True):
            progress_bar.update(len(chunk))
            content += chunk
    return (file_path, content)


def _save_file_map_fn(file_id, file_path, progress_bar, is_uploaded_job=False):
    endpoint = GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
        if not is_uploaded_job else \
        GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT

    download_url = endpoint + str(file_id)
    file_path.parents[0].mkdir(parents=True, exist_ok=True)

    with requests.get(download_url, stream=True) as request:
        with file_path.open("wb+") as f:
            for chunk in request.iter_content(chunk_size=1024 * 16):
                progress_bar.update(len(chunk))
                f.write(chunk)
