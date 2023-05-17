import numpy as np
import pandas as pd
from ioe.constants import (
    COLUMN_LATITUDE,
    COLUMN_LONGITUDE,
    COLUMN_TRAVEL,
    MAX_REQUESTS_PER_MINUTE,
    TFL_API_PREFIX,
)
from ioe.instructions.connection import create_connection_string
from numpy import typing as npt
from pyrate_limiter import FileLockSQLiteBucket
from requests import Response, Session
from requests_ratelimiter import LimiterAdapter

session = Session()
adapter = LimiterAdapter(
    per_minute=MAX_REQUESTS_PER_MINUTE, bucket_class=FileLockSQLiteBucket
)
session.mount(TFL_API_PREFIX, adapter)


def get_request_response(
    student: pd.Series,
    school: npt.NDArray[np.str_ | np.int_],
) -> Response:
    """
    Perform GET request and access the response
    """
    student_coord = ",".join(student[[COLUMN_LATITUDE, COLUMN_LONGITUDE]].astype(str))
    school_coord = ",".join(school[-2:].astype(str))
    connection_string = create_connection_string(
        student_coord, school_coord, mode=student[COLUMN_TRAVEL]
    )
    return session.get(connection_string)
