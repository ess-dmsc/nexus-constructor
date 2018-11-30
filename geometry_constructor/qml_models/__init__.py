def change_value(item, attribute_name, value):
    """
    Updates the value of an items attribute
    :param item: the object having an attribute updated
    :param attribute_name: the name of the attribute to update
    :param value: the value to set the attribute to
    :return: whether the attribute value was changed
    """
    current_value = getattr(item, attribute_name)
    different = value != current_value
    if different:
        setattr(item, attribute_name, value)
    return different
