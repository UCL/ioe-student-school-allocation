import logging
from pathlib import Path

import pandas as pd

_logger = logging.getLogger(__name__)


def save_output_journeys(
    data: list[tuple[int, str, int, str]], filepath: Path, *, save_output: bool = False
) -> pd.DataFrame:
    """Manipulate the successful data into desired CSV format saved as a feather file

    Args:
        data: The successful data to save
        filepath: The output filename
        save_output: Whether to not to save the output. Defaults to False.

    Returns:
        The successful journeys dataframe
    """
    df = pd.DataFrame(data, columns=["student", "school", "time", "message"])
    df = df.convert_dtypes()
    df.sort_values(by=["student", "school"], ignore_index=True, inplace=True)
    if save_output:
        _logger.info("Saving journey output to files")
        df.to_csv(filepath, index=False)
    return df


def save_output_failures(
    data: list[tuple[int, str, int, str]], filepath: Path, *, save_output: bool = False
) -> pd.DataFrame:
    """Manipulate the failed data into desired CSV format saved as a feather file

    Args:
        data: The failure data to save
        filepath: The output filename
        save_output: Whether to not to save the output. Defaults to False.

    Returns:
        The successful journeys dataframe
    """
    df = pd.DataFrame(data, columns=["student", "school", "code", "reason"])
    df = df.convert_dtypes()
    df["code"] = pd.to_numeric(df["code"], downcast="unsigned")
    df["reason"] = df["reason"].astype("category")
    df.sort_values(by=["student", "school", "code"], ignore_index=True, inplace=True)
    if save_output:
        _logger.info("Saving failure output to file")
        df.to_csv(filepath, index=False)
    return df
