from functools import lru_cache
from pathlib import Path

import pandas as pd

from settings.settings import get_settings


@lru_cache(maxsize=1)
def get_dataframe(data_path: Path | None = None) -> pd.DataFrame:
    if data_path is None:
        data_path = Path(get_settings().data_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Parquet file not found at {data_path.resolve()}")

    return pd.read_parquet(data_path, engine="pyarrow")