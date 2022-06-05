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
    return recursively_map_dict_keys(input_dict, lambda key: key_map.get(key, key))
