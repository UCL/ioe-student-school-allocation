import openrouteservice
from ioe.constants import OPENROUTESERVICE_API_KEY

_client = openrouteservice.Client(key=OPENROUTESERVICE_API_KEY)


def calculate_driving_time(
    student_latitude: int,
    student_longitude: int,
    school_latitude: int,
    school_longitude: int,
) -> int:
    """Calls the openrouteservice SDK and finds the minimum driving duration

    Args:
        student_latitude: the student latitude
        student_longitude: the student longitude
        school_latitude: the school latitude
        school_longitude: the school longitude

    Returns:
        The minimum driving duration in minutes for the student school pair
    """
    student_coords = (student_longitude, student_latitude)
    school_coords = (school_longitude, school_latitude)
    routes = _client.directions((student_coords, school_coords), profile="driving-car")
    return min(routes["routes"], key=lambda r: r["summary"]["duration"])
