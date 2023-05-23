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
        journey: _description_
        transport_mode: _description_

    Returns:
        _description_
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
        subject (str): _description_
        student (pd.Series): _description_
        school (dict): _description_
        data (dict): _description_

    Returns:
        tuple[int, str, int, str]: _description_
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
    """
    For a given student school pair give the failure reason
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
        subject (str): _description_
        student (pd.DataFrame): _description_
        school (dict[str, str  |  int]): _description_

    Returns:
        tuple[int, tuple[int, str, int, str]]: _description_
    """
    response = get_request_response(student, school)
    if response.status_code != requests.codes.OK:
        return response.status_code, _create_failure(subject, student, school, response)
    data = response.json()
    return response.status_code, _create_journey(subject, student, school, data)
