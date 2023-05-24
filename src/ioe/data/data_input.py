from pathlib import Path

import pandas as pd


def read_data(filepath: Path, *, nrows: int | None = None) -> list[str]:
    """Read in given file output subset if needed

    Args:
        filepath: The input data path
        nrows: The number of rows to read. Defaults to None.

    Returns:
        The input data
    """
    data = pd.read_csv(filepath)
    return data[:nrows] if nrows is not None else data
