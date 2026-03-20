def calculate_distance(point1, point2):
    return ((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2) ** 0.5

def calculate_midpoint(point1, point2):
    return Point((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)

def calculate_area_of_triangle(point1, point2, point3):
    return abs((point1.x * (point2.y - point3.y) + point2.x * (point3.y - point1.y) + point3.x * (point1.y - point2.y)) / 2.0)

def calculate_perimeter_of_triangle(point1, point2, point3):
    return (calculate_distance(point1, point2) + 
            calculate_distance(point2, point3) + 
            calculate_distance(point3, point1))

def project_point_onto_axis(point, axis_start, axis_end):
    axis_vector = (axis_end.x - axis_start.x, axis_end.y - axis_start.y)
    point_vector = (point.x - axis_start.x, point.y - axis_start.y)
    
    axis_length_squared = axis_vector[0] ** 2 + axis_vector[1] ** 2
    if axis_length_squared == 0:
        return axis_start  # Axis start and end are the same point
    
    projection_scale = (point_vector[0] * axis_vector[0] + point_vector[1] * axis_vector[1]) / axis_length_squared
    projected_x = axis_start.x + projection_scale * axis_vector[0]
    projected_y = axis_start.y + projection_scale * axis_vector[1]
    
    return Point(projected_x, projected_y)