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

def compute_active(pdf, min_reg):
    cell_agg = (
        pdf.groupby(["Motor energy", "cell_x", "cell_y"])
        .agg(cell_registrations=("registrations", "sum"))
        .reset_index()
    )

    active_cells = cell_agg[cell_agg["cell_registrations"] >= min_reg]

    return active_cells, cell_agg

def compute_static_latent_volume(
    enriched_pdf: pd.DataFrame,
    grid_size: float = 0.2,
    min_registrations: int = 10,
) -> pd.DataFrame:
    """Calculates static (Non Year-Over-Year) latent space volume.

    Counts unique active grid cells occupied across the entire selected range.
    """
    if enriched_pdf.empty:
        return pd.DataFrame(columns=["motor_energy", "latent_volume"])

    pdf = enriched_pdf.copy()
    pdf["cell_x"] = np.floor(pdf["z_1"] / grid_size).astype(int)
    pdf["cell_y"] = np.floor(pdf["z_2"] / grid_size).astype(int)

    active_cells, cell_agg = compute_active(pdf, min_registrations)

    static_volume = (
        active_cells.groupby("Motor energy")
        .agg(latent_volume=("cell_x", "count"))
        .reset_index()
        .rename(columns={"Motor energy": "motor_energy"})
    )

    return static_volume

def extract_baseline_factors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts unique consumer choices count (commercial name + engine capacity + kw power) per TIME_PERIOD and Motor energy.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["TIME_PERIOD", "Motor energy", "unique_choices"]
        )

    return (
        df.drop_duplicates(
            subset=[
                "TIME_PERIOD",
                "Motor energy",
                "commercial_name",
                "engine_capacity (cm3)",
                "engine_power (KW)",
            ]
        )
        .groupby(["TIME_PERIOD", "Motor energy"])
        .size()
        .reset_index(name="unique_choices")
    )


def compute_baseline_normalization(
    df: pd.DataFrame, factors_df: pd.DataFrame | None = None
) -> pd.DataFrame:
    """
    Computes normalized registrations (registrations / unique_choices).
    """
    if df.empty:
        return pd.DataFrame()

    if factors_df is None:
        factors_df = extract_baseline_factors(df)

    registrations_counts = (
        df.groupby(["TIME_PERIOD", "Motor energy"])["registrations"]
        .sum()
        .reset_index(name="registrations_count")
    )

    summary = factors_df.merge(
        registrations_counts, on=["TIME_PERIOD", "Motor energy"]
    )
    summary["baseline_normalized_registrations"] = (
        summary["registrations_count"] / summary["unique_choices"]
    )

    return summary

def extract_latent_volume_bubbles(
    df: pd.DataFrame,
    grid_size: float = 0.2,
    min_registrations: int = 20,
) -> list[dict]:
    """
    Build BubbleChart data from autoencoder latent-space volume.
    """

    if df.empty:
        return []

    required_columns = {
        "Motor energy",
        "z_1",
        "z_2",
        "registrations",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Latent volume calculation requires columns: {sorted(missing)}. "
            f"Missing: {sorted(missing)}"
        )

    pdf = df.copy()

    pdf["cell_x"] = np.floor(pdf["z_1"] / grid_size).astype(int)
    pdf["cell_y"] = np.floor(pdf["z_2"] / grid_size).astype(int)

    # determine which latent cells are sufficiently populated.
    active_cells, cell_agg = compute_active(pdf, min_registrations)

    # number of active cells in latent space per powertrain.
    volume = (
        active_cells.groupby("Motor energy", as_index=False)
        .agg(latent_volume=("cell_x", "size"))
    )

    powertrains = [
        item["name"]
        for item in get_motor_energy_colors()
    ]

    volume["energy"] = volume["Motor energy"].map(
        {name: i for i, name in enumerate(powertrains)}
    )

    volume = volume.dropna(subset=["energy"])
    volume["energy"] = volume["energy"].astype(int)

    volume["index"] = 1

    return volume[
        [
            "Motor energy",
            "index",
            "latent_volume",
        ]
    ].to_dict(orient="records")