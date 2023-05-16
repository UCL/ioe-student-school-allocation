from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import pgeocode
import plotly.express as px

LATITUDE = "latitude"
LONGITUDE = "longitude"
MATCHES_SCHOOL_ID = "allocation_school_id"
SCHOOL_ID = "SE2 PP: Code"
SCHOOL_POSTCODE = "SE2 PP: PC"
SCHOOL_SUFFIX = "_school"
STUDENT_ID = "ST: ID"
STUDENT_POSTCODE = "ST: Term PC"
STUDENT_SUFFIX = "_student"

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
        usecols=[SCHOOL_ID, SCHOOL_POSTCODE],
    ).convert_dtypes()
    # prepare whole student data
    students = pd.read_csv(
        _file_location.parents[1] / "data" / f"{subject}_students.csv",
        usecols=[STUDENT_ID, STUDENT_POSTCODE],
    ).convert_dtypes()
    # prepare spopt allocated data
    matches = pd.read_csv(
        _file_location.parent / f"{subject}_matches.csv",
        usecols=[
            STUDENT_ID,
            MATCHES_SCHOOL_ID,
        ],
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
    # merge students with the composite matches
    matches_merge_students = schools_merge_matches.merge(
        students, how="left", on=STUDENT_ID
    )
    # merge the result with the UK database to get school lat lon coords
    matches_merge_students[
        [f"{LATITUDE}{SCHOOL_SUFFIX}", f"{LONGITUDE}{SCHOOL_SUFFIX}"]
    ] = _nomi.query_postal_code(matches_merge_students[SCHOOL_POSTCODE].values)[
        [LATITUDE, LONGITUDE]
    ]
    # merge the result with the UK database to get student lat lon coords
    matches_merge_students[
        [f"{LATITUDE}{STUDENT_SUFFIX}", f"{LONGITUDE}{STUDENT_SUFFIX}"]
    ] = _nomi.query_postal_code(matches_merge_students[STUDENT_POSTCODE].values)[
        [LATITUDE, LONGITUDE]
    ]
    # remove unrequired columns
    return matches_merge_students.drop(columns=[SCHOOL_POSTCODE, STUDENT_POSTCODE])


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
            LATITUDE: df[
                [f"{LATITUDE}{SCHOOL_SUFFIX}", f"{LATITUDE}{STUDENT_SUFFIX}"]
            ].values.reshape(-1),
            LONGITUDE: df[
                [f"{LONGITUDE}{SCHOOL_SUFFIX}", f"{LONGITUDE}{STUDENT_SUFFIX}"]
            ].values.reshape(-1),
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
        lat=f"{LATITUDE}{SCHOOL_SUFFIX}",
        lon=f"{LONGITUDE}{SCHOOL_SUFFIX}",
        color_discrete_sequence=["red"],
    )
    # plot all students
    students = px.scatter_mapbox(
        df,
        lat=f"{LATITUDE}{STUDENT_SUFFIX}",
        lon=f"{LONGITUDE}{STUDENT_SUFFIX}",
        color_discrete_sequence=["blue"],
    )
    fig.add_trace(students.data[0])

    # connect the student-school pairs
    df_combined_lat_lon = _prepare_connecting_lines(df.dropna())
    for i in range(0, len(df_combined_lat_lon), 2):
        connection = px.line_mapbox(
            df_combined_lat_lon.loc[i : i + 1],
            lat=LATITUDE,
            lon=LONGITUDE,
            color_discrete_sequence=["black"],
        )
        fig.add_trace(connection.data[0])

    # prepare final output
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    filename = f"matched_student_school_pairs_{subject}"
    fig.write_html(_file_location.parent / f"{filename}.html")
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
