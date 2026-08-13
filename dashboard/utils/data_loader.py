from functools import lru_cache
from pathlib import Path
import pandas as pd
import torch
import numpy as np
from utils.model.VehicleAutoencoder import VehicleAutoencoder

from settings.settings import get_settings


@lru_cache(maxsize=1)
def get_dataframe(data_path: Path | None = None) -> pd.DataFrame:
    if data_path is None:
        data_path = Path(get_settings().data_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Parquet file not found at {data_path.resolve()}")

    return pd.read_parquet(data_path, engine="pyarrow")

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

# @lru_cache(maxsize=1)
def generate_latent_dataframe_pandas(
    pdf: pd.DataFrame, 
    checkpoint_path="utils/model/best_vehicle_autoencoder.ckpt", 
    scaler_path="utils/model/scaler_params.pt",
    device="cpu",
    batch_size=65536
) -> pd.DataFrame:
    """
    Pandas-native version of generate_latent_dataframe. 
    Applies conditional zeroing and runs the autoencoder.
    """
    device_obj = device
    model = VehicleAutoencoder.load_from_checkpoint(checkpoint_path).to(device_obj)
    model.eval()

    scaler_params = torch.load(scaler_path, weights_only=False)
    feature_cols = scaler_params["feature_names"]

    # Emulate the PySpark F.when() logic in Pandas
    df_zeroed = pdf.copy()
    is_electric = df_zeroed["Motor energy"] == "Electricity"
    is_ice = df_zeroed["Motor energy"].isin(["Petrol (excluding hybrids)", "Diesel (excluding hybrids)"])

    df_zeroed.loc[is_electric, "co2_emissions_WLTP (g/km)"] = 0.0
    df_zeroed.loc[is_electric, "engine_capacity (cm3)"] = 0.0
    df_zeroed.loc[is_ice, "electric_energy_consumption (Wh/km)"] = 0.0

    df_dropped = df_zeroed.dropna(subset=feature_cols).copy()
    
    # Handle edge case where no data remains
    if df_dropped.empty:
        df_dropped["z_1"] = []
        df_dropped["z_2"] = []
        return df_dropped

    X_raw = df_dropped[feature_cols].values.astype(np.float32)
    X_scaled = (X_raw - scaler_params["mean"]) / scaler_params["std"]

    latent_coords = []
    with torch.no_grad():
        for i in range(0, len(X_scaled), batch_size):
            batch_x = torch.tensor(X_scaled[i : i + batch_size], dtype=torch.float32, device=device_obj)
            latent_coords.append(model.encode(batch_x).cpu().numpy())

    latent_matrix = np.vstack(latent_coords)
    df_dropped["z_1"] = latent_matrix[:, 0]
    df_dropped["z_2"] = latent_matrix[:, 1]

    return df_dropped

# @lru_cache(maxsize=1)
def compute_grid_normalisation(
    df: pd.DataFrame, 
    grid_size: float = 0.2, 
    min_registrations: int = 10
) -> pd.DataFrame:
    """
    Computes latent space volume (normalisation factor) and normalized registrations.
    """
    pdf = df.copy()
    if pdf.empty:
        return pd.DataFrame(columns=["TIME_PERIOD", "Motor energy", "normalized_registrations"])

    pdf["cell_x"] = np.floor(pdf["z_1"] / grid_size).astype(int)
    pdf["cell_y"] = np.floor(pdf["z_2"] / grid_size).astype(int)

    cell_agg = (
        pdf.groupby(["TIME_PERIOD", "Motor energy", "cell_x", "cell_y"])
        .agg(
            cell_registrations=("registrations", "sum"),
            unique_variants=("variant", "nunique") if "variant" in pdf.columns else ("registrations", "count")
        )
        .reset_index()
    )

    active_cells = cell_agg[cell_agg["cell_registrations"] >= min_registrations]

    volume_df = (
        active_cells.groupby(["TIME_PERIOD", "Motor energy"])
        .agg(
            latent_volume=("cell_x", "count"),
            active_registrations=("cell_registrations", "sum")
        )
        .reset_index()
    )

    raw_totals = (
        pdf.groupby(["TIME_PERIOD", "Motor energy"])["registrations"]
        .sum()
        .reset_index()
        .rename(columns={"registrations": "total_raw_registrations"})
    )

    summary = pd.merge(volume_df, raw_totals, on=["TIME_PERIOD", "Motor energy"])
    summary["normalized_registrations"] = summary["total_raw_registrations"] / summary["latent_volume"]

    return summary

def round_data_to_two_decimals(data: list[dict]) -> list[dict]:
    return [
        {k: round(v, 2) if isinstance(v, float) else v for k, v in row.items()}
        for row in data
    ]