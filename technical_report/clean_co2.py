from pyspark.sql import SparkSession
from pathlib import Path
from pyspark.sql import functions as F
import country_converter as coco

CLEANED_DATA_DIR = Path("../data/cleaned")
PROCESSED_DATA_DIR = Path("../data")

spark = SparkSession.builder.appName("profiling").config("spark.sql.ansi.enabled", "false").config("spark.driver.memory", "16g").getOrCreate()
df = spark.read.parquet(f"{PROCESSED_DATA_DIR}/4_eea_co2_emissions_from_passenger_cars-001.parquet")

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
    "r": "registrations"
}

for old_col, new_col in column_mapping.items():
    df = df.withColumnRenamed(old_col, new_col)

eu27_2020 = ['BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE']

df = df.filter(df["member_state"].isin(eu27_2020))


num_cols = [
    "mass_in_running_order (kg)", "co2_emissions_WLTP (g/km)", 
    "engine_capacity (cm3)", "engine_power (KW)", "electric_energy_consumption (Wh/km)"
]
str_cols = ["member_state", "make", "commercial_name", "fuel_type", "fuel_mode"]
all_cols = str_cols + num_cols


df = df.na.drop(subset=str_cols)
not_needed = ["vehicle_family_id_number", "version", "make", "fuel_mode", "type", "variant"]
df = df.drop(*not_needed)

df = df.withColumn("fuel_type", F.lower(F.col("fuel_type")))
df = df.withColumn("fuel_type", F.trim(F.col("fuel_type")))
df = df.withColumn("fuel_type", F.regexp_replace(F.col("fuel_type"), "-", "/"))

unnecessary = ["unknown", "other"]
df = df.filter(~df.fuel_type.isin(unnecessary))

df = df.withColumn(
    "fuel_type",
    F.when(F.col("fuel_type") == "electric", "Electricity")
     .when(F.col("fuel_type") == "petrol phev", "Petrol plug-in Hybrid")
     .when(F.col("fuel_type").isin("petrol/electric", "hybrid/petrol/e"), "Petrol hybrid")
     .when(F.col("fuel_type") == "diesel/electric", "Diesel hybrid")
     .when(F.col("fuel_type") == "petrol", "Petrol (excluding hybrids)")
     .when(F.col("fuel_type") == "diesel", "Diesel (excluding hybrids)")
     .otherwise("Alternative/Other") 
)

df = df.filter(~F.col("manufacturer_name_eu_standard_denomination").isin("DUPLICATE", "OUT OF SCOPE", "UNKNOWN", "duplicate", "unknown"))
df = df.withColumn(
    "manufacturer_name_eu_standard_denomination",
    F.when(F.col("manufacturer_name_eu_standard_denomination") == "AUDI HUNGARIA", "AUDI AG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "AUDI SPORT", "AUDI AG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "BEE", "BEE BEE")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "BLUECAR ITALY", "BLUECAR")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "BMW GMBH", "BMW AG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "DONGFENG LIUZHOU", "DONGFENG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "DONGFENG MOTOR", "DONGFENG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "DONKEVOORT", "DONKERVOORT")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "DR MOTOR", "DR AUTOMOBILES")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "Duplicate", "DUPLICATE")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "FORD INDIA", "FORD MOTOR COMPANY")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "FORD MOTOR AUSTRALIA", "FORD MOTOR COMPANY")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "FORD WERKE GMBH", "FORD MOTOR COMPANY")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "Ford Motor Company", "FORD MOTOR COMPANY")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "GENERAL MOTORS COMPANY", "GENERAL MOTORS")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "GENERAL MOTORS HOLDINGS", "GENERAL MOTORS")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "GM ITALIA", "GENERAL MOTORS")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "GM KOREA", "GENERAL MOTORS")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "GM KOREA", "GENERAL MOTORS")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HONDA CHINA", "HONDA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HONDA MOTOR CO", "HONDA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HONDA THAILAND", "HONDA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HONDA TURKIYE", "HONDA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HONDA UK", "HONDA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HYUNDAI ASSAN", "HYUNDAI")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HYUNDAI ASSAN", "HYUNDAI")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HYUNDAI CZECH", "HYUNDAI")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HYUNDAI CZECH", "HYUNDAI")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HYUNDAI EUROPE", "HYUNDAI")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "HYUNDAI INDIA", "HYUNDAI")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "JIANGXI JIANGLING", "JIANGLING MOTOR")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "KIA SLOVAKIA", "KIA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "KIA SLOVAKIA", "KIA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "LADA FRANCE", "LADA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "LANZHOU ZHIDOU", "LANZHOU")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "MAGYAR SUZUKI", "SUZUKI MOTOR CORPORATION")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "MARUTI SUZUKI", "SUZUKI MOTOR CORPORATION")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "MAZDA EUROPE", "MAZDA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "MERCEDES AMG", "MERCEDES-BENZ AG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "MERCEDES-AMG", "MERCEDES-BENZ AG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "NISSAN AUTOMOTIVE EUROPE", "NISSAN")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "OPEL AUTOMOBILE", "OPEL")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "QUATTRO", "AUDI AG")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "RADICAL MOTOSPORT", "RADICAL MOTORSPORT")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "ROLLS-ROYCE", "ROLLS ROYCE")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "SAIC MAXUS", "SAIC MOTOR CORPORATION")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "SAIC MOTOR", "SAIC MOTOR CORPORATION")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "STELLANTIS EUROPE", "STELLANTIS AUTO")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "SUZUKI THAILAND", "SUZUKI MOTOR CORPORATION")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "TOYOTA MOTOR CORPORATION", "TOYOTA")
     .when(F.col("manufacturer_name_eu_standard_denomination") == "WUHAN LOTUS", "LOTUS")
     .otherwise(F.col("manufacturer_name_eu_standard_denomination"))
)

grouping_columns = [col for col in df.columns if col != "registrations"]
df = df.groupBy(*grouping_columns) \
               .agg(F.sum("registrations").alias("registrations"))
df = df.withColumnRenamed("member_state", "geo") \
                       .withColumnRenamed("fuel_type", "Motor energy") \
                       .withColumnRenamed("year", "TIME_PERIOD")
df = df.withColumn("Geopolitical entity (reporting)", F.udf(lambda x: coco.convert(names=x, to='name_short', not_found=None))(F.col("geo")))
df = df.withColumn("registrations", F.col("registrations").cast("integer"))

df = df.select(
    "geo",
    "Geopolitical entity (reporting)",
    "TIME_PERIOD",
    "registrations",
    "manufacturer_name_eu_standard_denomination",
    "commercial_name",
    "Motor energy",
    "mass_in_running_order (kg)",
    "co2_emissions_WLTP (g/km)",
    "engine_capacity (cm3)",
    "engine_power (KW)",
    "electric_energy_consumption (Wh/km)"
)

df.write.mode("overwrite") \
    .option("compression", "gzip") \
    .parquet(f"{CLEANED_DATA_DIR}/4_eea_co2_emissions_from_passenger_cars-001.parquet")