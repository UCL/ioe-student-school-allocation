from argparse import ArgumentParser, Namespace
from pathlib import Path

from ioe.data.data_input import read_data
from ioe.data.data_output import save_output_failures, save_output_journeys
from ioe.main import compute_all_pairs_journeys
from ioe.utils.constants import N_CORES


def _read_args() -> Namespace:
    """Read in CLI inputs.

    Returns:
        The CLI options output.
    """
    parser = ArgumentParser(
        description=("Constructs a set of student and school data from the main file")
    )
    parser.add_argument(
        "location",
        type=Path,
        help="data location",
    )
    parser.add_argument(
        "subject",
        type=str,
        help="placement subject",
    )
    return parser.parse_args()


def main() -> None:
    """
    computes the OD matrices for a given set of student school pairs
    """
    args = _read_args()
    students = read_data(args.location / f"{args.subject}_students.csv")
    schools = read_data(args.location / f"{args.subject}_schools.csv")
    journeys, failures = compute_all_pairs_journeys(
        args.subject,
        students,
        schools,
        n_cores=N_CORES,
    )
    save_output_journeys(
        journeys,
        args.location / f"{args.subject}_student_school_journeys.csv",
        save_output=True,
    )
    save_output_failures(
        failures,
        args.location / f"{args.subject}_student_school_failures.csv",
        save_output=True,
    )


if __name__ == "__main__":
    main()
