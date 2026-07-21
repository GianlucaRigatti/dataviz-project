from pathlib import Path
from pyspark.sql import SparkSession

PROCESSED_DATA_DIR = Path("../processed_data")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_DATA_DIR = Path("../clean_data")
CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)

spark = SparkSession.builder \
    .appName("profiling") \
    .config("spark.sql.ansi.enabled", "false") \
    .config("spark.driver.memory", "16g") \
    .getOrCreate()

cols = ["Country", "VFN", "Mh", "T", "Va", "Ve", "Mk", "Cn", "m (kg)", "Ewltp (g/km)", "Ft", "Fm", "ec (cm3)", "ep (KW)", "z (Wh/km)", "year"]

column_mapping = {
    "Country": "member_state",
    "VFN": "vehicle_family_id_number",
    "Mh": "manufacturer_name_eu_standard_denomination",
    "T": "type",
    "Va": "variant",
    "Ve": "version",
    "Mk": "make",
    "Cn": "commercial_name",
    "m (kg)": "mass_in_running_order (kg)",
    "Ewltp (g/km)": "co2_emissions_WLTP (g/km)",
    "Ft": "fuel_type",
    "Fm": "fuel_mode",
    "ec (cm3)": "engine_capacity (cm3)",
    "ep (KW)": "engine_power (KW)",
    "z (Wh/km)": "electric_energy_consumption (Wh/km)",
}

csv_name = "4_eea_co2_emissions_from_passenger_cars-001.csv"
path = f"../data/{csv_name}"

df = spark.read.csv(path, header=True, inferSchema=True).select(*cols)

for old_col, new_col in column_mapping.items():
    df = df.withColumnRenamed(old_col, new_col)

eu27_2020 = ['BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE']

df_only_eu = df.filter(df["member_state"].isin(eu27_2020))

df_only_eu.write.mode("overwrite") \
    .option("compression", "gzip") \
    .parquet(f"{CLEAN_DATA_DIR}/4_eea_co2_emissions_from_passenger_cars-001.parquet")

df.write.mode("overwrite") \
    .option("compression", "gzip") \
    .parquet(f"{PROCESSED_DATA_DIR}/4_eea_co2_emissions_from_passenger_cars-001.parquet")


