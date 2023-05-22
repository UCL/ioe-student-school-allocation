import openrouteservice
import pandas as pd

from ioe.constants import COLUMN_LATITUDE, COLUMN_LONGITUDE, OPENROUTESERVICE_API_KEY

_client = openrouteservice.Client(key=OPENROUTESERVICE_API_KEY)


def calculate_driving_time(student: pd.Series, school: dict[str, str | int]) -> dict:
    """Calls the openrouteservice SDK and finds the minimum driving duration

    Args:
        student: an individual student data
        school: an individual school data

    Returns:
        The minimum driving duration in minutes for the student school pair
    """
    coords = (
        (student[COLUMN_LONGITUDE], student[COLUMN_LATITUDE]),
        (school[COLUMN_LONGITUDE], school[COLUMN_LATITUDE]),
    )
    routes = _client.directions(coords, profile="driving-car")
    return min(routes["routes"], key=lambda r: r["summary"]["duration"])
