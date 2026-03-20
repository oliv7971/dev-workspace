def parse_date(date_str):
    """
    Parses a date string and normalizes it to the format YYYY-MM-DD.
    
    Args:
        date_str (str): The date string to parse.
        
    Returns:
        str: The normalized date string in YYYY-MM-DD format, or None if parsing fails.
    """
    from dateutil import parser

    try:
        # Attempt to parse the date string
        parsed_date = parser.parse(date_str)
        # Return the date in YYYY-MM-DD format
        return parsed_date.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        # Return None if parsing fails
        return None


def normalize_dates(date_list):
    """
    Normalizes a list of date strings to the format YYYY-MM-DD.
    
    Args:
        date_list (list): A list of date strings to normalize.
        
    Returns:
        list: A list of normalized date strings.
    """
    return [parse_date(date) for date in date_list if parse_date(date) is not None]