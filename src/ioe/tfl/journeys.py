import logging

import pandas as pd
import requests
from requests import Response

from ioe.constants import COLUMN_SCHOOL_ID, COLUMN_STUDENT_ID, COLUMN_TRAVEL
from ioe.tfl.api import get_request_response

_logger = logging.getLogger(__name__)


def _create_journey_instructions(
    journey: dict, *, transport_mode: str
) -> tuple[int, str]:
    """Find the duration and create the message for a single journey

    Args:
        journey: The successful journey
        transport_mode: Mode either "P" or "B"

    Returns:
        The duration in minutes and a route description
    """
    duration = journey["duration"]
    if transport_mode == "P":
        legs = journey["legs"]
        message = f"{legs[0]['instruction']['summary']}"
        message += "".join(f" THEN {leg['instruction']['summary']}" for leg in legs[1:])
    else:
        message = "Cycle"
    _logger.debug(message)
    return duration, message


def _create_journey(
    subject: str,
    student: pd.Series,
    school: dict,
    data: dict,
) -> tuple[int, str, int, str]:
    """Create final journey with the shortest leg for the student, school pair

    Args:
        subject: The school subject
        student: Individual student data
        school: Individual school data
        data: The output from the ORS API

    Returns:
        The student, school, duration, and output message
    """
    # find the number of journeys
    found_journeys = data["journeys"]
    _logger.info(
        f"Number of valid TfL journeys found: {len(found_journeys)} for "
        f"student: {student[COLUMN_STUDENT_ID]} -> school: "
        f"{school[COLUMN_SCHOOL_ID]}, subject {subject}"
    )

    # shortest journey
    shortest_journey = min(found_journeys, key=lambda j: j["duration"])
    duration, message = _create_journey_instructions(
        shortest_journey, transport_mode=student[COLUMN_TRAVEL]
    )

    # prepare the final output
    return student[COLUMN_STUDENT_ID], school[COLUMN_SCHOOL_ID], duration, message


def _create_failure(
    subject: str,
    student: pd.Series,
    school: dict,
    response: Response,
) -> tuple[int, str, int, str]:
    """For a given student school pair give the failure reason

    Args:
        subject: School subject
        student: Individual student data
        school: Individual school data
        response: The API response

    Returns:
        The student, school, reponse code, reason of failure
    """
    code = response.status_code
    reason = response.reason
    _logger.error(
        f"Status code: {code} for student: {student[COLUMN_STUDENT_ID]} "
        f"-> school: {school[COLUMN_SCHOOL_ID]}, subject: {subject}"
    )
    return student[COLUMN_STUDENT_ID], school[COLUMN_SCHOOL_ID], code, reason


def create_tfl_routes(
    subject: str, student: pd.DataFrame, school: dict[str, str | int]
) -> tuple[int, tuple[int, str, int, str]]:
    """Method to be executed by each process filling the same dictionary

    Args:
        subject: School subject
        student: Individual student data
        school: Individual school data

    Returns:
        Response code, and the journey/failure
    """
    response = get_request_response(student, school)
    if response.status_code != requests.codes.OK:
        return response.status_code, _create_failure(subject, student, school, response)
    data = response.json()
    return response.status_code, _create_journey(subject, student, school, data)
