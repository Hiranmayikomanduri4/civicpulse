"""
Geographic utility functions for distance calculation and proximity checks.
Uses the Haversine formula to compute geodesic distances between coordinate pairs.
"""
import math


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in meters.
    """
    # Earth radius in meters
    EARTH_RADIUS = 6371000.0

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = EARTH_RADIUS * c
    return round(distance, 2)


def format_distance(meters: float) -> str:
    """Format meters into a user-friendly string (meters or kilometers)."""
    if meters < 1000:
        return f"{int(meters)} meters"
    return f"{meters / 1000.0:.2f} km"


def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_meters: float = 150.0) -> bool:
    """Check if point 2 is within radius_meters of point 1."""
    return calculate_haversine_distance(lat1, lon1, lat2, lon2) <= radius_meters
