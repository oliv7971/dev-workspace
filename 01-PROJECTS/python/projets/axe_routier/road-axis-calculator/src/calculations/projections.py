def project_point_on_axis(point, axis):
    # Calculate the projection of a point onto the axis
    # Assuming axis is defined by two points (start and end)
    start, end = axis.start, axis.end
    axis_vector = (end.x - start.x, end.y - start.y)
    point_vector = (point.x - start.x, point.y - start.y)

    axis_length_squared = axis_vector[0] ** 2 + axis_vector[1] ** 2
    if axis_length_squared == 0:
        return start  # The axis is a point

    projection_scale = (point_vector[0] * axis_vector[0] + point_vector[1] * axis_vector[1]) / axis_length_squared
    projected_x = start.x + projection_scale * axis_vector[0]
    projected_y = start.y + projection_scale * axis_vector[1]

    return Point(projected_x, projected_y)

def project_multiple_points(points, axis):
    # Project multiple points onto the axis
    return [project_point_on_axis(point, axis) for point in points]