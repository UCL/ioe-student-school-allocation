import logging

import openrouteservice
import pandas as pd
import requests

from ioe.constants import (
    COLUMN_LATITUDE,
    COLUMN_LONGITUDE,
    COLUMN_SCHOOL_ID,
    COLUMN_STUDENT_ID,
    COLUMN_TRAVEL,
    MINUTES,
    OPENROUTESERVICE_BASE_URL,
    OPENROUTESERVICE_TRANSPORT_MODES,
)

_client = openrouteservice.Client(base_url=OPENROUTESERVICE_BASE_URL)
_logger = logging.getLogger(__name__)


def _create_journey_instructions(journey: dict) -> tuple[int, str]:
    """Find the duration and create the message for a single journey

    Args:
        journey: The successful journeys

    Returns:
        The minutes in duration and an output string
    """
    duration_mins = round(journey["summary"]["duration"] / MINUTES)
    return duration_mins, "Drive"


def _calculate_ors_times(student: pd.Series, school: dict[str, str | int]) -> dict:
    """Calls the openrouteservice SDK and finds the details of shortest routes

    Args:
        student: an individual student data
        school: an individual school data

    Returns:
        The details of the minimum routes
    """
    coords = (
        (student[COLUMN_LONGITUDE], student[COLUMN_LATITUDE]),
        (school[COLUMN_LONGITUDE], school[COLUMN_LATITUDE]),
    )
    return _client.directions(
        coords, profile=OPENROUTESERVICE_TRANSPORT_MODES[student[COLUMN_TRAVEL]]
    )


def create_ors_routes(
    subject: str, student: pd.DataFrame, school: dict
) -> tuple[int, tuple[int, str, int, str]]:
    """Creates the routes from the openrouteservice

    Args:
        subject: The subject data
        student: The student dataframe
        school: The shool dictionary

    Returns:
        The requests code and the output for the journey file
    """
    # use ORS SDK to get ORS data
    data = _calculate_ors_times(student, school)

    # find the number of journeys
    found_journeys = data["routes"]
    _logger.info(
        f"Number of valid ORS journeys found: {len(found_journeys)} for "
        f"student: {student[COLUMN_STUDENT_ID]} -> school: "
        f"{school[COLUMN_SCHOOL_ID]}, subject {subject}."
    )

    # shortest journey
    shortest_journey = min(found_journeys, key=lambda r: r["summary"]["duration"])
    duration, message = _create_journey_instructions(shortest_journey)

    # prepare the final output
    return requests.codes.OK, (
        student[COLUMN_STUDENT_ID],
        school[COLUMN_SCHOOL_ID],
        duration,
        message,
    )
