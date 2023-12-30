

def calculate_geometric_center(points):
    if not points:
        return 0, 0
    total_x = sum(point.x for point in points)
    total_y = sum(point.y for point in points)
    center_x = total_x / len(points)
    center_y = total_y / len(points)
    return center_x, center_y
