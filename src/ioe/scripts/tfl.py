from argparse import ArgumentParser

from ioe.data.data_input import read_data
from ioe.data.data_output import save_output_failures, save_output_journeys
from ioe.main import compute_all_pairs_journeys
from ioe.utils.constants import N_CORES


def main(subject: str) -> None:
    """
    computes the OD matrices for a given set of student school pairs
    """
    students = read_data(f"{subject}_students.csv")
    schools = read_data(f"{subject}_schools.csv")
    journeys, failures = compute_all_pairs_journeys(
        subject,
        students,
        schools,
        n_cores=N_CORES,
    )
    save_output_journeys(
        journeys,
        f"{subject}_student_school_journeys.csv",
        save_output=True,
    )
    save_output_failures(
        failures,
        f"{subject}_student_school_failures.csv",
        save_output=True,
    )


if __name__ == "__main__":
    parser = ArgumentParser(
        description=("Constructs a set of student and school data from the main file")
    )
    parser.add_argument(
        "subject",
        type=str,
        help="placement subject",
    )
    args = parser.parse_args()
    main(args.subject)
