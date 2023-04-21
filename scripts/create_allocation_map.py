from pathlib import Path

import pandas as pd
import plotly.express as px

_file_location = Path(__file__).resolve()

DATA_POSTCODE = "postcode"
MATCHES_SCHOOL_POSTCODE = "allocation_school_postcode"
SCHOOL_ID = "SE2 PP: Code"
SCHOOL_POSTCODE = "SE2 PP: PC"
STUDENT_ID = "ST: ID"
STUDENT_POSTCODE = "ST: Term PC"


def _read_data(
    subject: str, postcodes: str
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reads in the initial school, the matches from `spopt` and the
    UK database on postcodes and prepare the data for processing.

    Args:
        subject: The name of the subject.
        postcodes: The name of the postcode data.

    Returns:
        The three prepared dataframes.
    """
    # prepare whole school data
    schools = pd.read_csv(
        _file_location.parents[1] / "data" / f"{subject}_schools.csv",
        usecols=[SCHOOL_ID, SCHOOL_POSTCODE],
    ).convert_dtypes()
    # prepare spopt allocated data
    matches = pd.read_csv(
        _file_location.parent / f"{subject}_matches.csv",
        usecols=[
            STUDENT_ID,
            STUDENT_POSTCODE,
            MATCHES_SCHOOL_POSTCODE,
        ],
    ).convert_dtypes()
    matches[STUDENT_POSTCODE] = matches[STUDENT_POSTCODE].str.replace(" ", "")
    # prepare postcode to lat lon data
    postcodes = pd.read_csv(
        _file_location.parent / f"{postcodes}.csv", usecols=lambda x: x != "id"
    ).convert_dtypes()
    postcodes[DATA_POSTCODE] = postcodes[DATA_POSTCODE].str.replace(" ", "")
    return schools, matches, postcodes


def _prepare_data(
    schools: pd.DataFrame, matches: pd.DataFrame, postcodes: pd.DataFrame
) -> pd.DataFrame:
    """Merges the three dataframes to make a singular dataframe with
    student/school ID and the lat lon coordinates.

    Args:
        schools: All school data.
        matches: The matched student-school data.
        postcodes: The UK postcode data.

    Returns:
        The prepared dataframe of coordinates.
    """
    # merge all schools on the student matches
    school_merge_matches = schools.merge(
        matches, how="left", left_on=SCHOOL_POSTCODE, right_on=MATCHES_SCHOOL_POSTCODE
    ).drop(columns=MATCHES_SCHOOL_POSTCODE)
    # merge the result with the UK database to get school lat lon coords
    matches_merge_school_lat_lon = school_merge_matches.merge(
        postcodes, how="left", left_on=SCHOOL_POSTCODE, right_on=DATA_POSTCODE
    ).drop(columns=[DATA_POSTCODE, SCHOOL_POSTCODE])
    # merge the result with the UK database to get student lat lon coords
    return matches_merge_school_lat_lon.merge(
        postcodes,
        how="left",
        left_on=STUDENT_POSTCODE,
        right_on=DATA_POSTCODE,
        suffixes=("_school", "_student"),
    ).drop(columns=[DATA_POSTCODE, STUDENT_POSTCODE])


def _prepare_connecting_lines(df: pd.DataFrame) -> pd.DataFrame:
    """_summary_

    Args:
        df (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    return pd.DataFrame(
        {
            "ID": df[["SE2 PP: Code", "ST: ID"]].values.reshape(-1),
            "latitude": df[["latitude_school", "latitude_student"]].values.reshape(-1),
            "longitude": df[["longitude_school", "longitude_student"]].values.reshape(
                -1
            ),
        }
    )


def _prepare_plot(df: pd.DataFrame) -> None:
    """Creates the plot of points on a map.

    Args:
        df: The prepared datafame.
    """
    # plot all schools
    fig = px.scatter_mapbox(
        df,
        lat="latitude_school",
        lon="longitude_school",
        hover_data=SCHOOL_ID,
        labels={
            SCHOOL_ID: "School ID",
            "latitude_school": "Latitude School",
            "longitude_school": "Longitude School",
        },
        color_discrete_sequence=["red"],
    )
    # plot all students
    students = px.scatter_mapbox(
        df,
        lat="latitude_student",
        lon="longitude_student",
        hover_data=STUDENT_ID,
        labels={
            STUDENT_ID: "Student ID",
            "latitude_student": "Latitude Student",
            "longitude_student": "Longitude Student",
        },
        color_discrete_sequence=["blue"],
    )
    fig.add_trace(students.data[0])

    # connect the student-school pairs
    # df_combined_lat_lon = _prepare_connecting_lines(df.dropna())
    # for i in range(len(df_combined_lat_lon) // 2):
    #     connection = px.line_mapbox(
    #         df_combined_lat_lon.loc[i:i+1],
    #         lat="latitude",
    #         lon="longitude",
    #         color_discrete_sequence=["black"]
    #     )
    #     fig.add_traces(connection.data)

    # prepare final output
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


def main(*, subject: str, postcodes: str) -> None:
    """_summary_

    Args:
        filename (str): _description_
    """
    schools, matches, postoces = _read_data(subject, postcodes)
    df = _prepare_data(schools, matches, postoces)
    _prepare_plot(df)


if __name__ == "__main__":
    # UK postcode data taken from
    # https://www.freemaptools.com/download-uk-postcode-lat-lng.htm
    main(subject="example_subject", postcodes="ukpostcodes")
