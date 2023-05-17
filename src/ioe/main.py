from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from ioe.instructions.journeys import process_individual_student
from ioe.logger import logging


def compute_all_pairs_journeys(
    subject: str,
    students: pd.DataFrame,
    schools: pd.DataFrame,
    *,
    n_cores: int = 1,
) -> tuple[list[tuple[str, str, int, str]], list[tuple[str, str, str, int, str]]]:
    """
    Loop through all students and school to find the min journey time for each
    """
    logging.info(f"Start process with {n_cores} cores for subject {subject}")
    args = [(subject, students, school) for school in schools.values]
    with ProcessPoolExecutor(max_workers=n_cores) as e:
        futures = e.map(process_individual_student, args)

    # collect results from concurrency
    journeys: list[tuple[str, str, int, str]] = []
    failures: list[tuple[str, str, str, int, str]] = []
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
