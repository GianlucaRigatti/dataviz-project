# %%
from pyspark.sql import SparkSession
from pathlib import Path
from pyspark.sql import functions as F

import numpy as np
import pandas as pd
import torch
import pytorch_lightning as pl

from torch.utils.data import TensorDataset, DataLoader
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint

from VehicleAutoencoder import VehicleAutoencoder

CLEANED_DATA_DIR = Path("../data/cleaned")
PROCESSED_DATA_DIR = Path("../data")

MODEL_DIR = Path("models/vehicle_autoencoder")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_VAL_SPLIT = 0.8
SEED = 42

MAX_EPOCHS = 300
PATIENCE = 10

DEVICE = "cuda"

YEARS = range(2014, 2024)

spark = (
    SparkSession.builder
    .appName("vehicle_autoencoder")
    .config("spark.sql.ansi.enabled", "false")
    .config("spark.driver.memory", "16g")
    .getOrCreate()
)

df = spark.read.parquet(
    f"{CLEANED_DATA_DIR}/4c_eea_co2_emissions_from_passenger_cars-001.parquet"
)

df.show(10)

def prepare_vehicle_data(
    spark_df,
    train_val_split=0.8,
    seed=42,
    device="cuda",
):
    """
    Prepare the multi-year dataset for the training process.

    Returns:
        train_loader
        val_loader
        metadata_df
        scaler_params
    """

    feature_cols = [
        "mass_in_running_order (kg)",
        "co2_emissions_WLTP (g/km)",
        "engine_capacity (cm3)",
        "engine_power (KW)",
        "electric_energy_consumption (Wh/km)",
    ]

    metadata_cols = [
        "geo",
        "TIME_PERIOD",
        "registrations",
        "manufacturer_name_eu_standard_denomination",
        "commercial_name",
        "variant",
        "Motor energy",
    ]

    motor_col = F.col("Motor energy")

    is_electric = (
        motor_col == "Electricity"
    )

    is_ice = motor_col.isin(
        "Petrol (excluding hybrids)",
        "Diesel (excluding hybrids)",
    )

    df_zeroed = (
        spark_df
        .withColumn(
            "co2_emissions_WLTP (g/km)",
            F.when(
                is_electric,
                0.0
            ).otherwise(
                F.col("co2_emissions_WLTP (g/km)")
            )
        )
        .withColumn(
            "engine_capacity (cm3)",
            F.when(
                is_electric,
                0.0
            ).otherwise(
                F.col("engine_capacity (cm3)")
            )
        )
        .withColumn(
            "electric_energy_consumption (Wh/km)",
            F.when(
                is_ice,
                0.0
            ).otherwise(
                F.col("electric_energy_consumption (Wh/km)")
            )
        )
    )

    df_clean = df_zeroed.dropna(
        subset=feature_cols
    )

    pdf = df_clean.select(
        metadata_cols + feature_cols
    ).toPandas()

    if pdf.empty:
        raise ValueError(
            "No usable observations remain after preprocessing."
        )

    metadata_df = pdf[
        metadata_cols
    ].copy()

    X_raw = pdf[
        feature_cols
    ].values.astype(np.float32)

    np.random.seed(seed)

    n_samples = len(X_raw)

    indices = np.random.permutation(
        n_samples
    )

    split_idx = int(
        n_samples * train_val_split
    )

    train_idx = indices[:split_idx]
    val_idx = indices[split_idx:]

    metadata_df["split"] = "train"

    metadata_df.iloc[
        val_idx,
        metadata_df.columns.get_loc("split")
    ] = "val"

    mean = np.mean(
        X_raw[train_idx],
        axis=0
    )

    std = np.std(
        X_raw[train_idx],
        axis=0
    )

    std[std == 0.0] = 1.0

    X_scaled = (
        X_raw - mean
    ) / std

    scaler_params = {
        "mean": mean,
        "std": std,
        "feature_names": feature_cols,
    }

    device_obj = torch.device(
        device
        if torch.cuda.is_available()
        else "cpu"
    )

    X_train_tensor = torch.tensor(
        X_scaled[train_idx],
        dtype=torch.float32,
        device=device_obj,
    )

    X_val_tensor = torch.tensor(
        X_scaled[val_idx],
        dtype=torch.float32,
        device=device_obj,
    )

    print(
        f"Total observations: {len(X_raw):,}"
    )

    print(
        f"Training observations: {len(train_idx):,}"
    )

    print(
        f"Validation observations: {len(val_idx):,}"
    )

    print(
        f"Train tensor shape: {X_train_tensor.shape}"
    )

    print(
        f"Val tensor shape:   {X_val_tensor.shape}"
    )

    train_dataset = TensorDataset(
        X_train_tensor
    )

    val_dataset = TensorDataset(
        X_val_tensor
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=len(train_dataset),
        shuffle=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=len(val_dataset),
        shuffle=False,
    )

    return (
        train_loader,
        val_loader,
        metadata_df,
        scaler_params,
    )

def train_autoencoder(
    model,
    train_loader,
    val_loader,
    model_dir,
    max_epochs=300,
    patience=10,
):
    """
    Train ONE global autoencoder across all years.
    """

    early_stop_callback = EarlyStopping(
        monitor="val_loss",
        min_delta=1e-3,
        patience=patience,
        mode="min",
        verbose=True,
    )

    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        mode="min",
        save_top_k=1,
        filename="vehicle_autoencoder",
        dirpath=str(model_dir),
    )

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator=(
            "gpu"
            if torch.cuda.is_available()
            else "cpu"
        ),
        devices=1,
        callbacks=[
            early_stop_callback,
            checkpoint_callback,
        ],
        enable_progress_bar=True,
    )

    trainer.fit(
        model,
        train_dataloaders=train_loader,
        val_dataloaders=val_loader,
    )

    best_val_loss = (
        checkpoint_callback.best_model_score
    )

    if best_val_loss is not None:
        best_val_loss = (
            best_val_loss
            .detach()
            .cpu()
            .item()
        )

    return (
        trainer,
        checkpoint_callback.best_model_path,
        best_val_loss,
    )

torch.set_float32_matmul_precision("high")

year_df = df.filter(
    F.col("TIME_PERIOD").isin(
        list(YEARS)
    )
)

n_rows = year_df.count()

print(
    f"Raw rows for {min(YEARS)}-{max(YEARS)}: "
    f"{n_rows:,}"
)

if n_rows == 0:
    raise ValueError("No data found for the requested years.")


(
    train_loader,
    val_loader,
    metadata,
    scaler_params,
) = prepare_vehicle_data(
    year_df,
    train_val_split=TRAIN_VAL_SPLIT,
    seed=SEED,
    device=DEVICE,
)

n_samples = len(metadata)

print(
    f"Usable observations: {n_samples:,}"
)

if n_samples < 2:
    raise ValueError(
        "Not enough observations to train the autoencoder."
    )

scaler_path = (
    MODEL_DIR / "scaler.pt"
)

torch.save(
    scaler_params,
    scaler_path,
)

print(f"Global scaler saved to: {scaler_path}")

model = VehicleAutoencoder()

(
    trainer,
    best_model_path,
    best_val_loss,
) = train_autoencoder(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    model_dir=MODEL_DIR,
    max_epochs=MAX_EPOCHS,
    patience=PATIENCE,
)

print(f"Years: {min(YEARS)}-{max(YEARS)}")

print(f"Usable observations: {n_samples:,}")

print
(
    f"Training observations:  "
    f"{metadata['split'].eq('train').sum():,}"
)

print
(
    f"Validation observations:"
    f" {metadata['split'].eq('val').sum():,}"
)

print(f"Best validation loss: {best_val_loss}")
print(f"Checkpoint: {best_model_path}")
print(f"Scaler: {scaler_path}")