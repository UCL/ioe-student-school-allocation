import pandas as pd
from pyrate_limiter import FileLockSQLiteBucket
from requests import Response, Session
from requests_ratelimiter import LimiterAdapter

from ioe.constants import (
    COLUMN_LATITUDE,
    COLUMN_LONGITUDE,
    MAX_REQUESTS_PER_MINUTE,
    TFL_API_PREFIX,
)
from ioe.tfl.connection import create_connection_string

_session = Session()
_adapter = LimiterAdapter(
    per_minute=MAX_REQUESTS_PER_MINUTE, bucket_class=FileLockSQLiteBucket
)
_session.mount(TFL_API_PREFIX, _adapter)


def get_request_response(
    student: pd.Series,
    school: dict[str, str | int],
) -> Response:
    """Perform GET request and access the response

    Args:
        student: An individual student data
        school: An individual school data

    Returns:
        The API response
    """
    student_coord = ",".join(student[[COLUMN_LATITUDE, COLUMN_LONGITUDE]].astype(str))
    school_coord = ",".join(
        [f"{school[s]}" for s in [COLUMN_LATITUDE, COLUMN_LONGITUDE]]
    )
    connection_string = create_connection_string(
        student_coord,
        school_coord,
    )
    return _session.get(connection_string)
