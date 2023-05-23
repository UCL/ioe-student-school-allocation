from pathlib import Path

import pandas as pd


def read_data(filepath: Path, *, nrows: int | None = None) -> list[str]:
    """Read in given file output subset if needed

    Args:
        filepath: _description_
        nrows: _description_. Defaults to None.

    Returns:
        _description_
    """
    data = pd.read_csv(filepath)
    return data[:nrows] if nrows is not None else data
