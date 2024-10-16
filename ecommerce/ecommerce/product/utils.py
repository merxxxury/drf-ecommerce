def remove_empty_fields(data_dict: dict, fields_list: list) -> dict:
    """
    Remove empty fields from a dictionary.

    This function is typically used within a serializer's `to_representation`
    method to remove fields with empty values from the serialized JSON representation.

    Args:
        data_dict (dict): The dictionary containing serialized data.
        fields_list (list): A list of field names (strings) to check and potentially remove.

    Returns:
        dict: The modified dictionary with empty fields removed.
    """
    for field in fields_list:
        # Remove the field if its value is empty or evaluates to False
        if not data_dict[field]:
            data_dict.pop(field, None)

    return data_dict
