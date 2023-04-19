from ioe.utils.constants import TFL_API_PREFIX, TFL_APP_KEY
from ioe.utils.logger import logging


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


def create_connection_string(
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
    url = (
        f"{TFL_API_PREFIX}/{student}/to/{school}"
        f"?app_key={TFL_APP_KEY}{optional_queries}"
    )
    logging.debug(url)
    return url
