def calculate_offset(point, axis, lateral_displacement):
    """
    Calculate the new point offset from the given point along the axis.
    
    :param point: The original point to offset.
    :param axis: The axis along which the point is located.
    :param lateral_displacement: The distance to offset the point laterally.
    :return: A new point representing the offset position.
    """
    # Assuming axis has a method to get the direction vector
    direction = axis.get_direction_vector()
    
    # Calculate the normal vector (perpendicular to the direction)
    normal = (-direction[1], direction[0])  # 90 degrees rotation
    
    # Normalize the normal vector
    length = (normal[0]**2 + normal[1]**2) ** 0.5
    normal = (normal[0] / length, normal[1] / length)
    
    # Calculate the new coordinates
    new_x = point.x + normal[0] * lateral_displacement
    new_y = point.y + normal[1] * lateral_displacement
    
    return Point(new_x, new_y)

def calculate_multiple_offsets(points, axis, lateral_displacement):
    """
    Calculate multiple offsets for a list of points along the axis.
    
    :param points: A list of points to offset.
    :param axis: The axis along which the points are located.
    :param lateral_displacement: The distance to offset the points laterally.
    :return: A list of new points representing the offset positions.
    """
    return [calculate_offset(point, axis, lateral_displacement) for point in points]