import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers
    
    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
    except (ValueError, TypeError):
        return float('inf')

    # Convert coordinates to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine components
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
        
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    distance = R * c
    return distance
