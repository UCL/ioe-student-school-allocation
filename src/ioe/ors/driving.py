import openrouteservice
import pandas as pd

from ioe.constants import COLUMN_LATITUDE, COLUMN_LONGITUDE, OPENROUTESERVICE_API_KEY

_client = openrouteservice.Client(key=OPENROUTESERVICE_API_KEY)


def _calculate_driving_times(student: pd.Series, school: dict[str, str | int]) -> dict:
    """Calls the openrouteservice SDK and finds the details of shortest driving routes

    Args:
        student: an individual student data
        school: an individual school data

    Returns:
        The details of the minimum driving routes
    """
    coords = (
        (student[COLUMN_LONGITUDE], student[COLUMN_LATITUDE]),
        (school[COLUMN_LONGITUDE], school[COLUMN_LATITUDE]),
    )
    routes = _client.directions(coords, profile="driving-car")
    return min(routes["routes"], key=lambda r: r["summary"]["duration"])


# def create_ors_routes(student: pd.Series, school: dict[str, str | int]) -> dict:
#     """Calls the openrouteservice SDK and finds the minimum driving duration

#     Args:
#         student: an individual student data
#         school: an individual school data

#     Returns:

#     """
#     coords = (
#         (student[COLUMN_LONGITUDE], student[COLUMN_LATITUDE]),
#         (school[COLUMN_LONGITUDE], school[COLUMN_LATITUDE]),
#     )
#     routes = _client.directions(coords, profile="driving-car")
#     return min(routes["routes"], key=lambda r: r["summary"]["duration"])


def create_ors_routes(
    args: tuple[str, pd.DataFrame, dict[str, str | int]]
) -> tuple[list[tuple[str, str, int, str]], list[tuple[str, str, int, str]]]:
    """_summary_

    Args:
        args: _description_

    Returns:
        _description_
    """
    # so can map in parallel
    subject, students, school = args
