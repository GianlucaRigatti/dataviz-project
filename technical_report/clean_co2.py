from pyspark.sql import SparkSession
from pathlib import Path
from pyspark.sql import functions as F
import country_converter as coco
from itertools import chain

if __name__ == "__main__":
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
    country_dict = {code: coco.convert(names=code, to='name_short', not_found=None) for code in eu27_2020}

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

    df = df.withColumn("fuel_type", 
        F.regexp_replace(F.trim(F.lower(F.col("fuel_type"))), "-", "/")
    )

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

    name_map = {
        "AUDI HUNGARIA": "AUDI AG",
        "AUDI SPORT": "AUDI AG",
        "BEE": "BEE BEE",
        "BLUECAR ITALY": "BLUECAR",
        "BMW GMBH": "BMW AG",
        "DONGFENG LIUZHOU": "DONGFENG",
        "DONGFENG MOTOR": "DONGFENG",
        "DONKEVOORT": "DONKERVOORT",
        "DR MOTOR": "DR AUTOMOBILES",
        "Duplicate": "DUPLICATE",
        "FORD INDIA": "FORD MOTOR COMPANY",
        "FORD MOTOR AUSTRALIA": "FORD MOTOR COMPANY",
        "FORD WERKE GMBH": "FORD MOTOR COMPANY",
        "Ford Motor Company": "FORD MOTOR COMPANY",
        "GENERAL MOTORS COMPANY": "GENERAL MOTORS",
        "GENERAL MOTORS HOLDINGS": "GENERAL MOTORS",
        "GM ITALIA": "GENERAL MOTORS",
        "GM KOREA": "GENERAL MOTORS",
        "GM KOREA": "GENERAL MOTORS",
        "HONDA CHINA": "HONDA",
        "HONDA MOTOR CO": "HONDA",
        "HONDA THAILAND": "HONDA",
        "HONDA TURKIYE": "HONDA",
        "HONDA UK": "HONDA",
        "HYUNDAI ASSAN": "HYUNDAI",
        "HYUNDAI ASSAN": "HYUNDAI",
        "HYUNDAI CZECH": "HYUNDAI",
        "HYUNDAI CZECH": "HYUNDAI",
        "HYUNDAI EUROPE": "HYUNDAI",
        "HYUNDAI INDIA": "HYUNDAI",
        "JIANGXI JIANGLING": "JIANGLING MOTOR",
        "KIA SLOVAKIA": "KIA",
        "KIA SLOVAKIA": "KIA",
        "LADA FRANCE": "LADA",
        "LANZHOU ZHIDOU": "LANZHOU",
        "MAGYAR SUZUKI": "SUZUKI MOTOR CORPORATION",
        "MARUTI SUZUKI": "SUZUKI MOTOR CORPORATION",
        "MAZDA EUROPE": "MAZDA",
        "MERCEDES AMG": "MERCEDES-BENZ AG",
        "MERCEDES-AMG": "MERCEDES-BENZ AG",
        "NISSAN AUTOMOTIVE EUROPE": "NISSAN",
        "OPEL AUTOMOBILE": "OPEL",
        "QUATTRO": "AUDI AG",
        "RADICAL MOTOSPORT": "RADICAL MOTORSPORT",
        "ROLLS-ROYCE": "ROLLS ROYCE",
        "SAIC MAXUS": "SAIC MOTOR CORPORATION",
        "SAIC MOTOR": "SAIC MOTOR CORPORATION",
        "STELLANTIS EUROPE": "STELLANTIS AUTO",
        "SUZUKI THAILAND": "SUZUKI MOTOR CORPORATION",
        "TOYOTA MOTOR CORPORATION": "TOYOTA",
        "WUHAN LOTUS": "LOTUS"
    }

    df = df.replace(name_map, subset=["manufacturer_name_eu_standard_denomination"])

    grouping_columns = [col for col in df.columns if col != "registrations"]
    df = df.groupBy(*grouping_columns) \
                   .agg(F.sum("registrations").alias("registrations"))
    df = df.withColumnRenamed("member_state", "geo") \
                           .withColumnRenamed("fuel_type", "Motor energy") \
                           .withColumnRenamed("year", "TIME_PERIOD")

    mapping_expr = F.create_map([F.lit(x) for x in chain(*country_dict.items())])
    df = df.withColumn("Geopolitical entity (reporting)", mapping_expr[F.col("geo")])

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