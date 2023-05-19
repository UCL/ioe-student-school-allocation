import logging

_logger = logging.getLogger(__name__)

_formatter = logging.Formatter(
    "%(levelname)s [%(asctime)s] ioe: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)
_logger.addHandler(_console_handler)
_logger.setLevel("INFO")
_logger.propagate = False
