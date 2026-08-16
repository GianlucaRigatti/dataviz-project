from functools import lru_cache
from pathlib import Path
import pandas as pd
import torch
import numpy as np
from utils.model.VehicleAutoencoder import VehicleAutoencoder

from settings.settings import get_settings

MIN_REGISTRATIONS_DEFAULT = 5

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

@lru_cache(maxsize=1)
def get_motor_energy_plotly_colors() -> dict[str, str]:
    return {
        "Petrol (excluding hybrids)": "#E03131",
        "Diesel (excluding hybrids)": "#228BE6",
        "Electricity": "#12B886",
        "Petrol hybrid": "#FD7E14",
        "Diesel hybrid": "#15AABF",
        "Alternative/Other": "#868E96",
    }

# @lru_cache(maxsize=1)
def generate_latent_dataframe_pandas(
    pdf: pd.DataFrame,
    checkpoint_dir="utils/model/vehicle_autoencoder",
    device="cpu",
    batch_size=65536,
) -> pd.DataFrame:
    """
    Generate latent coordinates using the autoencoder.
    """

    if pdf.empty:
        return pdf.copy()

    required_columns = {
        "TIME_PERIOD",
        "Motor energy",
        "registrations",
    }

    missing = required_columns - set(pdf.columns)

    if missing:
        raise ValueError(
            f"Latent generation requires columns: {sorted(required_columns)}. "
            f"Missing: {sorted(missing)}"
        )

    checkpoint_dir = Path(checkpoint_dir)
    device_obj = torch.device(device)

    checkpoint_path = (
        checkpoint_dir / "vehicle_autoencoder.ckpt"
    )

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Global autoencoder checkpoint not found at "
            f"{checkpoint_path}"
        )

    model = (
        VehicleAutoencoder
        .load_from_checkpoint(
            str(checkpoint_path)
        )
        .to(device_obj)
    )

    model.eval()

    scaler_path = (
        checkpoint_dir / "scaler.pt"
    )

    if not scaler_path.exists():
        raise FileNotFoundError(
            f"Global scaler not found at "
            f"{scaler_path}"
        )

    scaler_params = torch.load(
        scaler_path,
        map_location="cpu",
        weights_only=False,
    )

    feature_cols = scaler_params["feature_names"]

    mean = np.asarray(
        scaler_params["mean"],
        dtype=np.float32,
    )

    std = np.asarray(
        scaler_params["std"],
        dtype=np.float32,
    )

    result_parts = []

    for year, year_pdf in pdf.groupby(
        "TIME_PERIOD",
        sort=True,
    ):

        year_zeroed = year_pdf.copy()

        is_electric = (
            year_zeroed["Motor energy"] == "Electricity"
        )

        is_ice = year_zeroed["Motor energy"].isin([
            "Petrol (excluding hybrids)",
            "Diesel (excluding hybrids)",
        ])

        year_zeroed.loc[
            is_electric,
            "co2_emissions_WLTP (g/km)"
        ] = 0.0

        year_zeroed.loc[
            is_electric,
            "engine_capacity (cm3)"
        ] = 0.0

        year_zeroed.loc[
            is_ice,
            "electric_energy_consumption (Wh/km)"
        ] = 0.0

        year_dropped = year_zeroed.dropna(
            subset=feature_cols
        ).copy()

        if year_dropped.empty:
            continue

        X_raw = year_dropped[
            feature_cols
        ].values.astype(np.float32)

        X_scaled = (
            X_raw - mean
        ) / std

        latent_coords = []

        with torch.no_grad():

            for i in range(
                0,
                len(X_scaled),
                batch_size,
            ):

                batch_x = torch.tensor(
                    X_scaled[
                        i:i + batch_size
                    ],
                    dtype=torch.float32,
                    device=device_obj,
                )

                latent = model.encode(
                    batch_x
                )

                latent_coords.append(
                    latent.detach()
                    .cpu()
                    .numpy()
                )

        latent_matrix = np.vstack(
            latent_coords
        )

        year_dropped["z_1"] = (
            latent_matrix[:, 0]
        )

        year_dropped["z_2"] = (
            latent_matrix[:, 1]
        )

        result_parts.append(
            year_dropped
        )

    if not result_parts:
        result = pdf.iloc[0:0].copy()

        result["z_1"] = pd.Series(
            dtype=float
        )

        result["z_2"] = pd.Series(
            dtype=float
        )

        return result

    return pd.concat(
        result_parts,
        ignore_index=True,
    )

# @lru_cache(maxsize=1)
def compute_grid_normalisation(
    df: pd.DataFrame,
    grid_size: float = 0.2,
    min_registrations: int = MIN_REGISTRATIONS_DEFAULT,
) -> pd.DataFrame:
    """
    Computes year-specific latent-space normalisation using the autoencoder.

    Grid occupancy is calculated independently for each year and
    Motor energy category.

    normalized_registrations =
        total registrations / active latent-space cells
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "TIME_PERIOD",
                "Motor energy",
                "latent_volume",
                "active_registrations",
                "total_raw_registrations",
                "normalized_registrations",
            ]
        )

    required_columns = {
        "TIME_PERIOD",
        "Motor energy",
        "z_1",
        "z_2",
        "registrations",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Grid normalisation requires columns: "
            f"{sorted(required_columns)}. "
            f"Missing: {sorted(missing)}"
        )

    pdf = df.copy()

    pdf["cell_x"] = np.floor(
        pdf["z_1"] / grid_size
    ).astype(int)

    pdf["cell_y"] = np.floor(
        pdf["z_2"] / grid_size
    ).astype(int)

    cell_agg = (
        pdf
        .groupby([
            "TIME_PERIOD",
            "Motor energy",
            "cell_x",
            "cell_y",
        ])
        .agg(
            cell_registrations=(
                "registrations",
                "sum",
            ),
            unique_variants=(
                "variant",
                "nunique",
            ) if "variant" in pdf.columns else (
                "registrations",
                "count",
            ),
        )
        .reset_index()
    )

    active_cells = cell_agg[
        cell_agg["cell_registrations"] >= min_registrations
    ]

    volume_df = (
        active_cells
        .groupby([
            "TIME_PERIOD",
            "Motor energy",
        ])
        .agg(
            latent_volume=(
                "cell_x",
                "size",
            ),
            active_registrations=(
                "cell_registrations",
                "sum",
            ),
        )
        .reset_index()
    )

    raw_totals = (
        pdf
        .groupby([
            "TIME_PERIOD",
            "Motor energy",
        ])["registrations"]
        .sum()
        .reset_index(
            name="total_raw_registrations"
        )
    )

    summary = volume_df.merge(
        raw_totals,
        on=[
            "TIME_PERIOD",
            "Motor energy",
        ],
        how="left",
    )

    summary["normalized_registrations"] = (
        summary["total_raw_registrations"]
        / summary["latent_volume"]
    )

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

def compute_latent_volumes(
    df: pd.DataFrame,
    grid_size: float = 0.2,
    min_registrations: int = 10,
) -> list[dict]:
    """
    Computes year-specific autoencoder normalisation factors.
    """

    if df.empty:
        return []

    required_columns = {
        "TIME_PERIOD",
        "Motor energy",
        "z_1",
        "z_2",
        "registrations",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Latent normalisation requires columns: "
            f"{sorted(required_columns)}. "
            f"Missing: {sorted(missing)}"
        )

    pdf = df.copy()

    pdf["cell_x"] = np.floor(
        pdf["z_1"] / grid_size
    ).astype(int)

    pdf["cell_y"] = np.floor(
        pdf["z_2"] / grid_size
    ).astype(int)

    cell_agg = (
        pdf.groupby(
            [
                "TIME_PERIOD",
                "Motor energy",
                "cell_x",
                "cell_y",
            ],
            as_index=False,
        )
        .agg(
            cell_registrations=(
                "registrations",
                "sum",
            )
        )
    )

    active_cells = cell_agg[
        cell_agg["cell_registrations"] >= min_registrations
    ]

    volume = (
        active_cells
        .groupby(
            [
                "TIME_PERIOD",
                "Motor energy",
            ],
            as_index=False,
        )
        .agg(
            latent_volume=(
                "cell_x",
                "size",
            )
        )
    )

    registrations = (
        pdf
        .groupby(
            [
                "TIME_PERIOD",
                "Motor energy",
            ],
            as_index=False,
        )
        .agg(
            total_registrations=(
                "registrations",
                "sum",
            )
        )
    )

    summary = registrations.merge(
        volume,
        on=[
            "TIME_PERIOD",
            "Motor energy",
        ],
        how="left",
    )

    summary["latent_volume"] = (
        summary["latent_volume"]
        .astype(float)
    )


    summary["normalized_registrations"] = np.where(
        summary["latent_volume"] > 0,
        summary["total_registrations"]
        / summary["latent_volume"],
        np.nan,
    )

    powertrains = [
        item["name"]
        for item in get_motor_energy_colors()
    ]

    years = sorted(
        pdf["TIME_PERIOD"]
        .dropna()
        .unique()
    )

    complete_index = pd.MultiIndex.from_product(
        [years, powertrains],
        names=[
            "TIME_PERIOD",
            "Motor energy",
        ],
    )

    summary = (
        summary
        .set_index(
            [
                "TIME_PERIOD",
                "Motor energy",
            ]
        )
        .reindex(complete_index)
        .reset_index()
    )

    return summary[
        [
            "TIME_PERIOD",
            "Motor energy",
            "latent_volume",
            "normalized_registrations",
        ]
    ].to_dict(
        orient="records"
    )