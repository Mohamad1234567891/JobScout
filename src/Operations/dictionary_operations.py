"""Small dictionary helpers used by the extraction pipeline.

Adapted from ShopWise's DictionaryOperations with standard Python naming.
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
