import logging
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
import requests

from ioe.constants import COLUMN_SCHOOL_ID, COLUMN_TRAVEL
from ioe.ors.routing import create_ors_routes
from ioe.tfl.journeys import create_tfl_routes

_logger = logging.getLogger(__name__)


def _process_individual_student(
    args: tuple[str, pd.DataFrame, dict[str, str | int]]
) -> tuple[list[tuple[int, str, int, str]], list[tuple[int, str, int, str]]]:
    """Method to be executed by each process filling the same dictionary.

    Args:
        args: The subject, students, and school data

    Returns:
        The successful journeys and the failed journeys
    """
    # so can map in parallel
    subject, students, school = args

    # initialise internal journeys and failures
    journeys: list[tuple[int, str, int, str]] = []
    failures: list[tuple[int, str, int, str]] = []

    _logger.info(f"New school: {school[COLUMN_SCHOOL_ID]}, subject {subject}")
    for _, student in students.iterrows():
        status_code, route = (
            create_tfl_routes(subject, student, school)
            if student[COLUMN_TRAVEL] == "P"
            else create_ors_routes(subject, student, school)
        )
        if status_code == requests.codes.OK:
            journeys.append(route)
        else:
            failures.append(route)
    return journeys, failures


def compute_all_pairs_journeys(
    subject: str,
    students: pd.DataFrame,
    schools: pd.DataFrame,
    *,
    n_cores: int = 1,
) -> tuple[list[tuple[int, str, int, str]], list[tuple[int, str, int, str]]]:
    """Loop through all students and school to find the min journey time for each.

    Args:
        subject: The subject
        students: The students dataframe
        schools: The schools dataframe
        n_cores (optional): The number of cores to parallelise over. Defaults to 1.

    Returns:
        The full successful journeys and failed journeys
    """
    _logger.info(f"Start process with {n_cores} cores for subject {subject}")
    args = [(subject, students, school) for school in schools.to_dict("records")]
    with ProcessPoolExecutor(max_workers=n_cores) as e:
        futures = e.map(_process_individual_student, args)

    # collect results from concurrency
    journeys: list[tuple[int, str, int, str]] = []
    failures: list[tuple[int, str, int, str]] = []
    for journey, failure in futures:
        journeys.extend(journey)
        failures.extend(failure)

    assert len(students) * len(schools) == len(journeys) + len(  # noqa: S101
        failures
    ), (
        f"there is a mistmatch in the number of students {len(students)}/schools "
        f"{len(schools)} and the number of found journeys {len(journeys)}/failures "
        f"{len(failures)} for subject {subject}"
    )

    return journeys, failures
