def is_valid_coordinate(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_valid_distance(value):
    return isinstance(value, (int, float)) and value >= 0

def is_valid_tunnel_dimensions(width, height):
    return is_valid_distance(width) and is_valid_distance(height)

def is_valid_axis_length(length):
    return is_valid_distance(length)

def validate_point_input(x, y):
    return is_valid_coordinate(x) and is_valid_coordinate(y)

def validate_axis_input(length):
    return is_valid_axis_length(length)

def validate_tunnel_input(width, height):
    return is_valid_tunnel_dimensions(width, height)