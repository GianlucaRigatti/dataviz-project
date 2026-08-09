# Technical Report

This directory contains the notebooks and scripts used for the data preprocessing, validation, and exploratory analysis presented in the technical report deliverable.

## 🚀 Getting Started

### Prerequisites

> [!IMPORTANT]
> This project requires **Python 3.11+**.

> [!WARNING]
> Running the preprocessing notebooks may require significant memory and computational resources, especially for large datasets. A minimum of 32 GB of RAM is recommended.

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



### 🗃️ Datasets

> [!IMPORTANT]
> The raw datasets should be placed in the appropriate `data/` directory before running the notebooks.

1. [Eurostat - New passenger cars by type of motor energy and engine size](https://ec.europa.eu/eurostat/databrowser/view/road_eqr_carmot/default/table?lang=en&category=road.road_eqr)
2. [Eurostat - New passenger cars by type of motor energy](https://ec.europa.eu/eurostat/databrowser/view/road_eqr_carpda/default/table?lang=en&category=road.road_eqr)
3. [UNECE - New passenger car registrations by fuel type (detailed)](https://w3.unece.org/PXWeb2015/pxweb/en/STAT/STAT__40-TRTRANS__03-TRRoadFleet/09_en_TRRoadNewPasVh_r.px/)
4. [EEA - Monitoring of CO2 emissions from passenger cars Regulation (EU) 2019/631](https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b)

### Note on computational resources

## 📂 Directory Structure

| File / Directory | Description |
| :--- | :--- |
| 📁 **`img/`** | Figures generated for the technical report deliverable. |
| 📁 **`reports/`** | Output directory for dataset reports generated using `fg-data-profiling`. |
| 🪐 **`1_dataset_analysis_eurostat_new_passenger_cars_by_type_of_motor_energy_and_engine_size.ipynb`**<br>🪐 **`2_dataset_analysis_eurostat_new_passenger_cars_by_type_of_motor_energy.ipynb`**<br>🪐 **`3_dataset_analysis_unece_new_passenger_car_registrations_by_fuel_type_(detailed).ipynb`**<br>🪐 **`4_dataset_graphing_eea_co2_emissions_from_passenger_cars.ipynb`** | Notebooks covering dataset description and preprocessing for the Eurostat, UNECE, and EEA datasets. Generate the clean (`c`) datasets in the `data/cleaned` folder. |
| 🪐  