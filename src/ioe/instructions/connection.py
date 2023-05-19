import logging

import openrouteservice
from ioe.constants import MINUTES, OPENROUTESERVICE_API_KEY, TFL_API_PREFIX, TFL_APP_KEY

_client = openrouteservice.Client(key=OPENROUTESERVICE_API_KEY)
_logger = logging.getLogger(__name__)


def _handle_transport_modes(transport_mode: str) -> tuple[str, str]:
    """
    For the problem at hand there are three valid options,
    prepare the input to the connection string function.

    >>> import requests
    >>> [m["modeName"] for m in requests.get(\
        "https://api.tfl.gov.uk/Journey/Meta/Modes").json()]
    """
    match transport_mode:
        case "B":
            mode = "cycle"
            cycle_preference = "allTheWay"
        case "C":
            # TODO: find correct mode or a different API
            mode = "private-car"
            cycle_preference = "none"
        case "P":
            mode = (
                # "black-cab-as-customer,"
                # "black-cab-as-driver,"
                "bus,"
                "cable-car,"
                "coach,"
                # "cycle,"
                # "cycle-hire,"
                "dlr,"
                # "electric-car,"
                "elizabeth-line,"
                # "goods-vehicle-as-driver,"
                "interchange-keep-sitting,"
                "interchange-secure,"
                "international-rail,"
                # "motorbike-scooter,"
                "national-rail,"
                "overground,"
                # "plane,"
                # "private-car,"
                # "private-coach-as-customer,"
                # "private-coach-as-driver,"
                # "private-hire-as-customer,"
                # "private-hire-as-driver,"
                "replacement-bus,"
                "river-bus,"
                # "river-tour,"
                # "taxi,"
                "tram,"
                "tube,"
                "walking,"
            )
            cycle_preference = "none"
        case _:
            raise ValueError(
                "`transport_mode` must be either `B` (bike), `C` (car) "
                f"or `P` (public transport) - found `{transport_mode}`"
            )
    return mode, cycle_preference


def _create_connection_string_tfl(  # noqa: PLR0913
    student: str,
    school: str,
    *,
    mode: str,
    accessibilityPreference: str = "noRequirements",  # noqa: N803
    adjustment: str = "tripLast",
    alternativeCycle: bool = False,  # noqa: N803
    alternativeWalking: bool = False,  # noqa: N803
    applyHtmlMarkup: bool = False,  # noqa: N803
    bikeProficiency: str = "moderate",  # noqa: N803
    calcOneDirection: bool = True,  # noqa: N803
    cyclePreference: str = "allTheWay",  # noqa: N803
    date: str = "",
    fromName: str = "",  # noqa: N803
    journeyPreference: str = "leastTime",  # noqa: N803
    maxTransferMinutes: str = "",  # noqa: N803
    maxWalkingMinutes: str = "",  # noqa: N803
    nationalSearch: bool = True,  # noqa: N803
    routeBetweenEntrances: bool = True,  # noqa: N803
    taxiOnlyTrip: bool = False,  # noqa: N803
    time: str = "0800",
    timeIs: str = "arriving",  # noqa: N803
    toName: str = "",  # noqa: N803
    useMultiModalCall: bool = False,  # noqa: N803
    useRealTimeLiveArrivals: bool = False,  # noqa: N803
    via: str = "",
    viaName: str = "",  # noqa: N803
    walkingOptimization: bool = True,  # noqa: N803
    walkingSpeed: str = "average",  # noqa: N803
) -> str:
    """
    Creates the optional arguments for the TfL API

    Full API options:
    >>> import requests
    >>> requests.get('https://api.tfl.gov.uk/swagger/docs/v1').json()['paths']\
        ['/Journey/JourneyResults/{from}/to/{to}']['get']['parameters']
    """
    # retrieve all inputs
    inputs = dict(locals())
    # remove irrelevant option for API
    del inputs["student"], inputs["school"]
    # override custom options
    inputs["mode"], inputs["cyclePreference"] = _handle_transport_modes(mode)
    # prepare optinal queries
    optional_queries = "".join(
        f"&{k}={v}" for (k, v) in inputs.items() if v != ""  # noqa: PLC1901
    )
    return (
        f"{TFL_API_PREFIX}/{student}/to/{school}"
        f"?app_key={TFL_APP_KEY}{optional_queries}"
    )


def _create_connection_string_openrouteservice(
    student: tuple[int, int],
    school: tuple[int, int],
) -> int:
    """Calls the openrouteservice SDK and finds the minimum driving duration

    Args:
        student: (student_longitude, student_latitude)
        school: (school_longitude, school_latitude)

    Returns:
        The minimum driving duration in minutes for the student school pair
    """
    routes = _client.directions((student, school), profile="driving-car")
    shortest_journey = min(routes["routes"], key=lambda r: r["summary"]["duration"])
    return shortest_journey["summary"]["duration"] / MINUTES


def create_connection_string(
    student_lat: int,
    student_lon: int,
    school_lat: int,
    school_lon: int,
    transport_mode: str,
) -> str:
    """
    Creates the API request URL for the appropriate mode-based domain.
    """
    url = (
        _create_connection_string_openrouteservice(
            (student_lon, student_lat), (school_lon, school_lat)
        )
        if transport_mode == "C"
        else _create_connection_string_tfl(
            ",".join([f"{st}" for st in (student_lat, student_lon)]),
            ",".join([f"{st}" for st in (school_lat, school_lon)]),
            mode=transport_mode,
        )
    )
    _logger.debug(url)
    return url
