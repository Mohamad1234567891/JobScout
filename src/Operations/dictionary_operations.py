"""
This file is part of JobScout, an open-source job-search and job-match
engine that scrapes LinkedIn and scores every posting against your profile.

Copyright (c) 2026 Muhammed Bekiroğlu and the JobScout contributors.

Original JobScout repository: https://github.com/Mohamad1234567891/JobScout

Muhammed Bekiroğlu (JobScout team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Small dictionary helpers used by the extraction pipeline.


"""


def get_list_of_values_of_key_from_dictionary_list(key, dictionaries):
    """Collects every value of the given key from a list of dictionaries.

    Args:
        key: The key whose values should be collected.
        dictionaries: A list of dictionaries.

    Returns:
        list: All values found under that key, in list order.
    """
    return [element[key] for element in dictionaries if key in element]
