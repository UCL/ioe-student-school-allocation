import logging

import pandas as pd
import requests
from requests import Response

from ioe.constants import COLUMN_SCHOOL_ID, COLUMN_STUDENT_ID, COLUMN_TRAVEL
from ioe.ors.driving import calculate_driving_journeys
from ioe.tfl.api import get_request_response

_logger = logging.getLogger(__name__)


def _create_journey_instructions(journey: dict) -> tuple[int, str]:
    """
    Find the duration and create the message for a single journey
    """
    duration = journey["duration"]
    legs = journey["legs"]
    message = f"{legs[0]['instruction']['summary']}"
    message += "".join(f" THEN {leg['instruction']['summary']}" for leg in legs[1:])
    _logger.debug(message)
    return duration, message


def _create_journey(
    subject: str,
    student: pd.Series,
    school: dict,
    data: dict,
) -> tuple[str, str, int, str]:
    """
    Create final journey with the shortest leg for the student, school pair
    """
    # find the number of journeys
    found_journeys = data["journeys"]
    _logger.info(
        f"Number of valid journeys found: {len(found_journeys)} for student: "
        f"{student[COLUMN_STUDENT_ID]} -> school: {school[COLUMN_SCHOOL_ID]}, "
        f"subject {subject}"
    )

    # shortest journey
    shortest_journey = min(found_journeys, key=lambda j: j["duration"])
    duration, message = _create_journey_instructions(shortest_journey)

    # prepare the final output
    return student[COLUMN_STUDENT_ID], school[COLUMN_SCHOOL_ID], duration, message


def _create_failure(
    subject: str,
    student: pd.Series,
    school: dict,
    response: Response,
) -> tuple[str, str, str, int, str]:
    """
    For a given student school pair give the failure reason
    """
    code = response.status_code
    reason = response.reason
    _logger.error(
        f"Status code: {code} for student: {student[COLUMN_STUDENT_ID]} "
        f"-> school: {school[COLUMN_SCHOOL_ID]}, subject: {subject}"
    )
    return (
        student[COLUMN_STUDENT_ID],
        school[COLUMN_SCHOOL_ID],
        student[COLUMN_TRAVEL],
        code,
        reason,
    )


def process_individual_student(
    args: tuple[str, pd.DataFrame, dict[str, str | int]]
) -> tuple[list[tuple[str, str, int, str]], list[tuple[str, str, str, int, str]]]:
    """
    method to be executed by each process filling the same dictionary
    """
    # so can map in parallel
    subject, students, school = args

    # initialise internal journeys and failures
    journeys: list[tuple[str, str, int, str]] = []
    failures: list[tuple[str, str, str, int, str]] = []

    _logger.info(f"New school: {school[COLUMN_SCHOOL_ID]}, subject {subject}")
    for _, student in students.iterrows():
        if student[COLUMN_TRAVEL] == "C":
            data = calculate_driving_journeys(student, school)
        else:
            response = get_request_response(
                student,
                school,
            )
            if response.status_code == requests.codes.ok:
                data = response.json()
                journeys.append(_create_journey(subject, student, school, data))
            else:
                failures.append(_create_failure(subject, student, school, response))
    return journeys, failures
