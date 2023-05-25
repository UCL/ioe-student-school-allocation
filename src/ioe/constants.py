import os

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
MAX_REQUESTS_PER_MINUTE = 250
MINUTES = 60
N_CORES = int(os.getenv("N_CORES", default="1"))
OPENROUTESERVICE_BASE_URL = os.getenv("OPENROUTESERVICE_BASE_URL")
OPENROUTESERVICE_TRANSPORT_MODES = {"B": "cycling-regular", "C": "driving-car"}
TFL_API_PREFIX = "https://api.tfl.gov.uk/Journey/JourneyResults"
TFL_APP_KEY = os.getenv("TFL_APP_KEY")
VALUE_COMPLETED = "completed"
VALUE_DO_NOT_USE = "do not use"
VALUE_NOT_APPLICABLE = "not applicable"
VALUE_NOT_KNOWN = "not known"

if TFL_APP_KEY is None:
    error = "Need to set 'TFL_APP_KEY'"
    raise OSError(error)

if OPENROUTESERVICE_BASE_URL is None:
    error = "Need to set 'OPENROUTESERVICE_BASE_URL'"
    raise OSError(error)
