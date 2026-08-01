from pathlib import Path
from pyspark.sql import SparkSession

PROCESSED_DATA_DIR = Path("../data")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# create the directory even if this specific script does not use it
CLEANED_DATA_DIR = Path("../data/cleaned")
CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

spark = SparkSession.builder \
    .appName("profiling") \
    .config("spark.sql.ansi.enabled", "false") \
    .config("spark.driver.memory", "16g") \
    .getOrCreate()

csv_name = "4_eea_co2_emissions_from_passenger_cars-001.csv"
path = f"../data/{csv_name}"

cols = ["Country", "VFN", "Mh", "T", "Va", "Ve", "Mk", "Cn", "m (kg)", "Ewltp (g/km)", "Ft", "Fm", "ec (cm3)", "ep (KW)", "z (Wh/km)", "year", "r"]

df = spark.read.csv(path, header=True, inferSchema=True).select(*cols)

df.write.mode("overwrite") \
    .option("compression", "gzip") \
    .parquet(f"{PROCESSED_DATA_DIR}/4_eea_co2_emissions_from_passenger_cars-001.parquet")