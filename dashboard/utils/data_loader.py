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

    return _add_eu27_aggregate(pd.read_parquet(data_path, engine="pyarrow"))

def _add_eu27_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    if "EU27_2020" in df["geo"].unique():
        return df

    eu27_df = (
        df.groupby(["TIME_PERIOD", "Motor energy"], as_index=False)["registrations"]
        .sum()
    )
    eu27_df["geo"] = "EU27_2020"
    eu27_df["Geopolitical entity (reporting)"] = "European Union (EU27)"
    return pd.concat([df, eu27_df], ignore_index=True)

@lru_cache(maxsize=1)
def get_motor_energy_colors() -> list[dict]:
    return [
        {
            "name": "Petrol (excluding hybrids)",
            "color": "red.6"
        }, {
            "name": "Diesel (excluding hybrids)",
            "color": "blue.6"
        }, {
            "name": "Electricity",
            "color": "teal.6"
        }, {
            "name": "Petrol hybrid",
            "color": "orange.6"
        }, {
            "name": "Diesel hybrid",
            "color": "cyan.6"
        }, {
            "name": "Alternative/Other",
            "color": "gray.6"
        }
    ]