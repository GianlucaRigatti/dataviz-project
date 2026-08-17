<div align="center">

<img src="assets/favicon-logo.png" height=128 width="auto" />
<h1 style="font-weight: 900;">About Car Market Trends</h1>

Developed by Gianluca Rigatti and Giuseppe Screnci for the *Data Visualisation Lab* course.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-306998?style=for-the-badge&logo=python&logoColor=white)
![fg-data-profiling](https://img.shields.io/badge/fg--data--profiling-10B981?style=for-the-badge&logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-F29111?style=for-the-badge&logo=apachespark&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-0EA5E9?style=for-the-badge&logo=docker&logoColor=white)
![Dash|Plotly](https://img.shields.io/badge/Dash|Plotly-0F172A?style=for-the-badge&logo=plotly&logoColor=white)
![Dash%20Mantine%20Components](https://img.shields.io/badge/Dash%20Mantine%20Components-14B8A6?style=for-the-badge&logo=mantine&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-0B132B?style=for-the-badge&logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-EA580C?style=for-the-badge&logo=jupyter&logoColor=white)

</div>

## 🌱🚗 About the Project

This project aims to develop a data visualisation solution for exploring the evolution of new passenger car registrations in Europe, with a particular focus on the transition towards more sustainable power train technologies.

The project includes the data preprocessing and validation steps applied to the [EEA's *Monitoring of CO2 emissions from passenger cars Regulation (EU) 2019/631*](https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b) dataset used to support the development of an interactive dashboard.

The central question guiding our analysis is:
>"Is the observed increase in electrified vehicles driven by genuine growth in demand, national incentives and taxation rules, or is it largely a consequence of the decline in petrol and diesel vehicle offerings?"

<div align="center">

  <img src="assets/overview-desktop.png" width="68%" alt="Dashboard desktop interface">
  &nbsp;&nbsp;&nbsp;
  <img src="assets/overview-mobile.png" width="20%" alt="Dashboard mobile interface">

</div>

> [!TIP]
> **🚀 TL;DR - Run with Docker**
>
> ```bash
> docker build -t my-dashboard .
> docker run -p 8050:8050 my-dashboard
> ```
>
> Open **http://localhost:8050** in your browser.
> See [`📄 dashboard/README.md`](dashboard/README.md) for detailed instructions and the Python virtual environment setup.

## 📂 Repository Structure

> [!IMPORTANT]
> See [`📄 dashboard/README.md`](dashboard/README.md) for instructions on running the dashboard and [`📄 technical_report/README.md`](technical_report/README.md) for informations on the preprocessing steps and analyses carried out for the technical report deliverable.

```text
.
├── 📂 assets/              # Assets for the repo
├── 📂 dashboard/           # Source code for the dashboard
│   └── 📄 README.md
├── 📂 data/                # Raw datasets
│   └── 📂 cleaned/         # Preprocessed datasets
├── 📂 docs/                # Deliverables [.pdf]
├── 📂 technical_report/    # Preprocessing and analysis scripts
│   └── 📄 README.md
└── 📄 README.md
```