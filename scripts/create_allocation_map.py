from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import pgeocode
import plotly.express as px

LATITUDE_COL = "latitude"
LONGITUDE_COL = "longitude"
MATCHES_SCHOOL_ID = "allocation_school_id"
SCHOOL_ID = "SE2 PP: Code"
SCHOOL_LATITUDE = "latitude_school"
SCHOOL_LONGITUDE = "longitude_school"
SCHOOL_POSTCODE = "SE2 PP: PC"
STUDENT_ID = "ST: ID"
STUDENT_LATITUDE = "latitude_student"
STUDENT_LONGITUDE = "longitude_student"
STUDENT_POSTCODE = "ST: Term PC"

_file_location = Path(__file__).resolve()
_nomi = pgeocode.Nominatim("GB_full")


def _read_data(
    subject: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reads in the initial school, the matches from `spopt` and the
    UK database on postcodes and prepare the data for processing.

    Args:
        subject: The name of the subject.

    Returns:
        The three prepared dataframes.
    """
    # prepare whole school data
    schools = pd.read_csv(
        _file_location.parents[1] / "data" / f"{subject}_schools.csv",
        usecols=[SCHOOL_ID, LATITUDE_COL, LONGITUDE_COL],
    ).convert_dtypes()
    # prepare whole student data
    students = pd.read_csv(
        _file_location.parents[1] / "data" / f"{subject}_students.csv",
        usecols=[STUDENT_ID, LATITUDE_COL, LONGITUDE_COL],
    ).convert_dtypes()
    # prepare spopt allocated data
    matches = pd.read_csv(
        _file_location.parents[1] / "data" / f"{subject}_matches.csv",
        usecols=[STUDENT_ID, MATCHES_SCHOOL_ID],
    ).convert_dtypes()
    return schools, students, matches


def _prepare_data(
    schools: pd.DataFrame,
    students: pd.DataFrame,
    matches: pd.DataFrame,
) -> pd.DataFrame:
    """Merges the three dataframes to make a singular dataframe with
    student/school ID and the lat lon coordinates.

    Args:
        schools: All school data.
        students: All students data.
        matches: The matched student-school data.

    Returns:
        The prepared dataframe of coordinates.
    """
    # merge all schools on the student matches
    schools_merge_matches = schools.merge(
        matches, how="left", left_on=SCHOOL_ID, right_on=MATCHES_SCHOOL_ID
    ).drop(columns=MATCHES_SCHOOL_ID)
    schools_merge_matches = schools_merge_matches.rename(
        columns={LONGITUDE_COL: SCHOOL_LONGITUDE, LATITUDE_COL: SCHOOL_LATITUDE}
    )
    # merge students with the composite matches
    matches_merge_students = schools_merge_matches.merge(
        students, how="left", on=STUDENT_ID
    )
    matches_merge_students = matches_merge_students.rename(
        columns={LONGITUDE_COL: STUDENT_LONGITUDE, LATITUDE_COL: STUDENT_LATITUDE}
    )
    # remove NAs
    return matches_merge_students.dropna()


def _prepare_connecting_lines(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares the dataframe in a format such that lines can be drawn on the map.

    Args:
        df: The prepared dataframe with NaNs removed.

    Returns:
        A dataframe alternating with school row followed by a student row.
    """
    return pd.DataFrame(
        {
            "ID": df[[SCHOOL_ID, STUDENT_ID]].values.reshape(-1),
            LATITUDE_COL: df[[SCHOOL_LATITUDE, STUDENT_LATITUDE]].values.reshape(-1),
            LONGITUDE_COL: df[[SCHOOL_LONGITUDE, STUDENT_LONGITUDE]].values.reshape(-1),
        }
    )


def _prepare_plot(subject: str, df: pd.DataFrame) -> None:
    """Creates the plot of points on a map.

    Args:
        subject: The name of the subject to process.
        df: The prepared datafame.
    """
    # plot all schools
    fig = px.scatter_mapbox(
        df,
        lat=SCHOOL_LATITUDE,
        lon=SCHOOL_LONGITUDE,
        color_discrete_sequence=["red"],
    )
    # plot all students
    students = px.scatter_mapbox(
        df,
        lat=STUDENT_LATITUDE,
        lon=STUDENT_LONGITUDE,
        color_discrete_sequence=["blue"],
    )
    fig.add_trace(students.data[0])

    # connect the student-school pairs
    df_combined_lat_lon = _prepare_connecting_lines(df.dropna())
    for i in range(0, len(df_combined_lat_lon), 2):
        connection = px.line_mapbox(
            df_combined_lat_lon.loc[i : i + 1],
            lat=LATITUDE_COL,
            lon=LONGITUDE_COL,
            color_discrete_sequence=["black"],
        )
        fig.add_trace(connection.data[0])

    # prepare final output
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    filename = f"matched_student_school_pairs_{subject}"
    fig.write_html(_file_location.parents[1] / "plot" / f"{filename}.html")
    fig.show(config={"toImageButtonOptions": {"filename": filename}})


def main(subject: str) -> None:
    """Creates a plotly map of all schools and lines
    connecting the matched students.

    Args:
        subject: The name of the subject.
    """
    schools, students, matches = _read_data(subject)
    df = _prepare_data(schools, students, matches)
    _prepare_plot(subject, df)


if __name__ == "__main__":
    # read in subject
    parser = ArgumentParser(
        description=("Creates the visualisation of points on a map per subject")
    )
    parser.add_argument(
        "subject",
        type=str,
        help="placement subject",
    )
    args = parser.parse_args()
    main(args.subject)
