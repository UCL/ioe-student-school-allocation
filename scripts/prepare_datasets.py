from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import pgeocode

COLUMN_COUNT = "Count"
COLUMN_LATITUDE = "latitude"
COLUMN_LONGITUDE = "longitude"
COLUMN_PLACEMENT_STATUS = "PL: Status"
COLUMN_SCHOOL_ID = "SE2 PP: Code"
COLUMN_SCHOOL_POSTCODE = "SE2 PP: PC"
COLUMN_STUDENT_ID = "ST: ID"
COLUMN_STUDENT_POSTCODE = "ST: Term PC"
COLUMN_STUDENT_PRIORITY = "ST: Allocation Priority"
COLUMN_SUBJECT = "PL: Subject"
COLUMN_TRAVEL = "Travel"
VALUE_COMPLETED = "completed"
VALUE_DO_NOT_USE = "do not use"
VALUE_NOT_APPLICABLE = "not applicable"
VALUE_NOT_KNOWN = "not known"

SCHOOL_COLUMNS = [
    COLUMN_SCHOOL_ID,
    COLUMN_LATITUDE,
    COLUMN_LONGITUDE,
    COLUMN_SUBJECT,
    COLUMN_COUNT,
]
STUDENT_COLUMNS = [
    COLUMN_STUDENT_ID,
    COLUMN_LATITUDE,
    COLUMN_LONGITUDE,
    COLUMN_SUBJECT,
    COLUMN_TRAVEL,
    COLUMN_STUDENT_PRIORITY,
]

_data_location = Path(__file__).resolve().parent
_nomi = pgeocode.Nominatim("GB_full")


def _convert_postcode_to_lat_lon(
    df: pd.DataFrame, postcode_column: str
) -> pd.DataFrame:
    """Converts a list of GB postcodes to latitude longitude coordinates

    Args:
        df: Input dataframe which includes postcode column
        postcode_column: A list of full GB postcodes

    Returns:
        A dataframe containing all the latitude and longitude
    """
    postcodes = df[postcode_column].values
    return _nomi.query_postal_code(postcodes)[[COLUMN_LATITUDE, COLUMN_LONGITUDE]]


def _prepare_school_priority_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Prepares the school priority column

    The priority column for schools has the following:
    * i.e. `2 (use)` to be replaced wirh `2`
    * mark those `Do not use` but `Completed` as `2`
    * Remaining `Do not use` to be removed
    * `Not applicable` to be removed
    * `Not known` to be replaced with `2`

    Args:
        df: The input dataframe
        column: The priority column

    Returns:
        The prepared prioirity column
    """
    df = df.copy()
    # overide some do not use columns
    rows_to_overide = (df[COLUMN_PLACEMENT_STATUS].str.lower() == VALUE_COMPLETED) & (
        df[column].str.lower() == VALUE_DO_NOT_USE
    )
    df.loc[rows_to_overide, column] = "2"
    # remove these columns
    df = df.loc[~df[column].str.lower().isin((VALUE_DO_NOT_USE, VALUE_NOT_APPLICABLE))]
    # replace value with 2
    df.loc[df[column].str.lower() == VALUE_NOT_KNOWN, column] = "2"
    # split into just numeric values
    df.loc[:, column] = df.loc[:, column].str.split(expand=True)[0]
    # fix index
    return df.convert_dtypes().reset_index(drop=True)


def _count_duplicate_schools(df: pd.DataFrame) -> pd.DataFrame:
    """Duplicate schools within a sub-subject should be counted and removed

    Args:
        df: Input dataframe

    Returns:
        The dataframe with duplicate schools changed to a count column
    """
    df[COLUMN_COUNT] = df[COLUMN_SCHOOL_ID].map(df[COLUMN_SCHOOL_ID].value_counts())
    return df.drop_duplicates(subset=COLUMN_SCHOOL_ID)


def _parepare_school_data(df: pd.DataFrame, subject: str) -> None:
    """Prepares the student data and saves the output

    Args:
        df: The input dataframe
        subject: The given subject column
    """
    df = df.copy()
    # prepare priority column
    school_priority = f"{subject.upper()[:3]} priority"
    new_columns = [*SCHOOL_COLUMNS, school_priority]
    # read_data
    df = (
        df.dropna(subset=COLUMN_SCHOOL_POSTCODE)
        .sort_values(by=COLUMN_SCHOOL_ID)
        .reset_index(drop=True)
    )
    # remove descriptions from priority column
    df = _prepare_school_priority_column(df, school_priority)
    # convert postcodes to lat lon
    df[[COLUMN_LATITUDE, COLUMN_LONGITUDE]] = _convert_postcode_to_lat_lon(
        df, COLUMN_SCHOOL_POSTCODE
    )
    # split by sub-subject
    for sub_subject, sub_data in df.groupby(df[COLUMN_SUBJECT]):
        df = _count_duplicate_schools(sub_data)
        filename = sub_subject.replace(": ", "_").lower()
        df[new_columns].reset_index(drop=True).to_csv(
            _data_location / f"{filename}_schools.csv", index=False
        )


def _parepare_student_data(df: pd.DataFrame) -> None:
    """Prepares the student data and saves the output

    Args:
        df: The input dataframe
    """
    df = df.copy()
    # read data
    df = (
        df.dropna(subset=COLUMN_STUDENT_POSTCODE)
        .sort_values(by=COLUMN_STUDENT_ID)
        .convert_dtypes()
        .reset_index(drop=True)
    )
    # create a travel mode column for API
    df[[COLUMN_STUDENT_PRIORITY, COLUMN_TRAVEL]] = df[COLUMN_STUDENT_PRIORITY].apply(
        lambda x: pd.Series(list(x))
    )
    # convert postcodes to lat lon
    df[[COLUMN_LATITUDE, COLUMN_LONGITUDE]] = _convert_postcode_to_lat_lon(
        df, COLUMN_STUDENT_POSTCODE
    )
    # split by sub-subject
    for sub_subject, sub_data in df.groupby(df[COLUMN_SUBJECT]):
        filename = sub_subject.replace(": ", "_").lower()
        sub_data[STUDENT_COLUMNS].reset_index(drop=True).to_csv(
            _data_location / f"{filename}_students.csv", index=False
        )


def main(filename: str) -> None:
    """Prepares the school and student data for each subject

    Args:
        filename: The input filename
    """
    df = pd.read_excel(_data_location / filename, sheet_name=None)
    for subject, data in df.items():
        _parepare_school_data(data, subject)
        _parepare_student_data(data)


if __name__ == "__main__":
    parser = ArgumentParser(
        description=("Constructs a set of student and school data from the main file")
    )
    parser.add_argument(
        "filename",
        type=str,
        help="master dataset",
    )
    args = parser.parse_args()
    main(args.filename)
