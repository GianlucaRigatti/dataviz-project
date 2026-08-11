# Technical Report

This directory contains the notebooks and scripts used for the data preprocessing, validation, and exploratory analysis presented in the technical report deliverable.

## 🚀 Getting Started

### 🗃️ Dataset Sources

Download the following datasets, rename them as indicated below, and place them in the `data/` directory:

1. [Eurostat - New passenger cars by type of motor energy and engine size](https://ec.europa.eu/eurostat/databrowser/view/road_eqr_carmot/default/table?lang=en&category=road.road_eqr) as *"1_eurostat_new_passenger_cars_by_type_of_motor_energy_and_engine_size.csv"*
2. [Eurostat - New passenger cars by type of motor energy](https://ec.europa.eu/eurostat/databrowser/view/road_eqr_carpda/default/table?lang=en&category=road.road_eqr) as *"2_eurostat_new_passenger_cars_by_type_of_motor_energy.csv"*
3. [UNECE - New passenger car registrations by fuel type (detailed)](https://w3.unece.org/PXWeb2015/pxweb/en/STAT/STAT__40-TRTRANS__03-TRRoadFleet/09_en_TRRoadNewPasVh_r.px/) as *"3_unece_new_passenger_car_registrations_by_fuel type_(detailed).csv"*
4. [EEA - Monitoring of CO2 emissions from passenger cars Regulation (EU) 2019/631](https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b) as *"4_eea_co2_emissions_from_passenger_cars.csv"*

### ⚙️ Prerequisites

> [!IMPORTANT]
> This project requires **Python 3.11+**.

> [!WARNING]
> Running the preprocessing notebooks may require significant memory and computational resources, especially for the large EEA dataset. A minimum of 32 GB of RAM is recommended.

1. Navigate to this directory:
   ```bash
   cd technical_report
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv

    # On macOS / Linux:
    source venv/bin/activate

    # On Windows (CMD / PowerShell):
    .\venv\Scripts\activate
    ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 💾 Obtaining the Preprocessed Datasets

> [!IMPORTANT]
> The raw datasets should be placed in the appropriate `data/` directory before running the scripts.

To obtain the final cleaned datasets used for the analyses, first run the `export_co2_to_parquet.py` script, then run the `'dataset_analysis'` notebooks to generate the cleaned datasets directly into the `data/cleaned/` folder.

> [!NOTE]
> The raw EEA CSV dataset is approximately 17 GB. After conversion to the more efficient Parquet format, the CSV file can be removed to save disk space.

## 📂 Directory Structure

> [!NOTE]
> The scripts and notebooks are intended to be executed from the `technical_report/` directory, to avoid path issues.

| File / Directory | Description |
| :--- | :--- |
| 📁&nbsp;**`img/`** | Figures generated for the technical report deliverable. |
| 📁&nbsp;**`reports/`** | Output directory for dataset reports generated using [`fg-data-profiling`](https://github.com/data-centric-ai-community/fg-data-profiling). |
| 🪐&nbsp;**`1_dataset_analysis_eurostat_new_passenger_cars_by_type_of_motor_energy_and_engine_size.ipynb`**<br>🪐&nbsp;**`2_dataset_analysis_eurostat_new_passenger_cars_by_type_of_motor_energy.ipynb`**<br>🪐&nbsp;**`3_dataset_analysis_unece_new_passenger_car_registrations_by_fuel_type_(detailed).ipynb`**<br>🪐&nbsp;**`4_dataset_analysis_eea_co2_emissions_from_passenger_cars.ipynb`** | Notebooks covering dataset description and preprocessing for the Eurostat, UNECE, and EEA datasets. |
| 🪐&nbsp;**`4_dataset_graphing_eea_co2_emissions_from_passenger_cars.ipynb`** | Notebook used for generating the figures for the technical report for the preprocessed EEA dataset. |
| 🪐&nbsp;**`4_null_counts_eea_co2_emissions_from_passenger_cars.ipynb`** | Notebook used for comparing null values counts in the original and preprocessed EEA dataset. |
| 🪐&nbsp;**`4_time_series_analysis_eea_co2_emissions_from_passenger_cars.ipynb`** | Notebook used for conducting time series analysis on the preprocessed EEA dataset. |
| 🪐&nbsp;**`autoencoder.ipynb`** | Notebook for training our autoencoder using [`lightning`](https://github.com/lightning-ai/pytorch-lightning). |
| 🪐&nbsp;**`baseline_normalisation.ipynb`** | Notebook for the baseline normalisation approach for the preprocessed EEA dataset to identify user choice. |
| 🐍&nbsp;**`export_co2_to_parquet.py`** | Script for exporting the EEA dataset from CSV to Parquet format. |
| 🪐&nbsp;**`fg-dp_co2-report_generator.ipynb`** | Notebook for generating the EEA report using [`fg-data-profiling`](https://github.com/data-centric-ai-community/fg-data-profiling). |
| 🐍&nbsp;**`fg-dp_reports_generator.py`** | Script for generating the Eurostat and UNECE dataset reports using [`fg-data-profiling`](https://github.com/data-centric-ai-community/fg-data-profiling). |
| 🪐&nbsp;**`reduction.ipynb`** | Notebook for testing dimensionality reduction capabilities of the encoder module from our trained autoencoder. |
| 🪐&nbsp;**`validation.ipynb`** | Notebook for validating the preprocessed EEA dataset against the chosen Eurostat dataset. |
| 🐍&nbsp;**`VehicleAutoencoder.py`** | Implementation of the autoencoder's model class using [`lightning`](https://github.com/lightning-ai/pytorch-lightning). |