from argparse import ArgumentParser, Namespace
from pathlib import Path

from ioe.constants import N_CORES
from ioe.data.data_input import read_data
from ioe.data.data_output import save_output_failures, save_output_journeys
from ioe.main import compute_all_pairs_journeys

_data_location = Path(__file__).resolve().parents[3] / "data"


def _read_args() -> Namespace:
    """Read in CLI inputs.

    Returns:
        The CLI options output.
    """
    parser = ArgumentParser(
        description=("Constructs a set of student and school data from the main file")
    )
    parser.add_argument(
        "subject",
        type=str,
        help="placement subject",
    )
    return parser.parse_args()


def main() -> None:
    """Computes the OD matrices for a given set of student school pairs"""
    args = _read_args()
    students = read_data(_data_location / f"{args.subject}_students.csv")
    schools = read_data(_data_location / f"{args.subject}_schools.csv")
    journeys, failures = compute_all_pairs_journeys(
        args.subject,
        students,
        schools,
        n_cores=N_CORES,
    )
    save_output_journeys(
        journeys,
        _data_location / f"{args.subject}_student_school_journeys.csv",
        save_output=True,
    )
    save_output_failures(
        failures,
        _data_location / f"{args.subject}_student_school_failures.csv",
        save_output=True,
    )


if __name__ == "__main__":
    main()
