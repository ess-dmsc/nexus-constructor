import re


def generate_unique_name(base: str, items: list):
    """
    Generates a unique name for a new item using a common base string

    :param base: The generated name will be the base string, followed by a number if required
    :param items: The named items to avoid generating a matching name with. Each must have a 'name' attribute
    """
    regex = f"^{re.escape(base)}\\d*$"
    similar_names = [item.name for item in items if re.match(regex, item.name)]
    if len(similar_names) == 0 or base not in similar_names:
        return base
    # find the highest number in use, and go one higher
    tailing_numbers = [int(name[len(base) :]) for name in similar_names if name != base]
    return base + str(max(tailing_numbers) + 1) if tailing_numbers else base + "1"
