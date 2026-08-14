import dash
from dash import callback, ctx, Input, Output
import dash_mantine_components as dmc
import pandas as pd

from views.overview_view import OverviewView
from utils.data_loader import get_dataframe, get_motor_energy_colors, generate_latent_dataframe_pandas, compute_grid_normalisation, round_data_to_two_decimals, extract_baseline_factors, compute_baseline_normalization

class OverviewController:
    def __init__(self):
        self.view = OverviewView()
        self._load_data()
        self._register_callbacks()

    def _load_data(self):
        self.df = get_dataframe()
        self.min_year = int(self.df["TIME_PERIOD"].min())
        self.max_year = int(self.df["TIME_PERIOD"].max())

        geo_df = self.df[~self.df["geo"].isin(["EU27_2020", "EU28", "EU"])][["geo", "Geopolitical entity (reporting)"]].drop_duplicates()
        
        self.geo_options = [
            {"value": row["geo"], "label": row["Geopolitical entity (reporting)"]}
            for _, row in geo_df.iterrows()
        ]
        
        self.geo_options.sort(key=lambda x: x["label"])
        self.geo_options.insert(0, {"value": "EU27_2020", "label": "European Union (EU27)"})
        self.default_geo = "EU27_2020"

    def _get_chart_payload(
        self,
        years: list[int],
        region: str
    ) -> tuple[list[dict], list[dict], list[dict], dict]:

        if not years or not region:
            return [], [], [], {}

        min_y, max_y = years

        if region == "EU27_2020":
            filtered = self.df[
                (self.df["TIME_PERIOD"] >= min_y) &
                (self.df["TIME_PERIOD"] <= max_y)
            ]
        else:
            filtered = self.df[
                (self.df["geo"] == region) &
                (self.df["TIME_PERIOD"] >= min_y) &
                (self.df["TIME_PERIOD"] <= max_y)
            ]

        if filtered.empty:
            return [], [], [], {}

        pivot_df = filtered.pivot_table(
            index="TIME_PERIOD",
            columns="Motor energy",
            values="registrations",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        pivot_df.rename(
            columns={"TIME_PERIOD": "year"},
            inplace=True
        )

        raw_chart_data = pivot_df.to_dict(
            orient="records"
        )

        baseline_factors = extract_baseline_factors(
            filtered
        )

        baseline_summary = compute_baseline_normalization(
            filtered,
            factors_df=baseline_factors
        )

        baseline_summary.rename(
            columns={"TIME_PERIOD": "year"},
            inplace=True
        )

        wide_df = baseline_summary.pivot(
            index="year",
            columns="Motor energy",
            values="baseline_normalized_registrations"
        ).reset_index()

        baseline_chart_data = wide_df.to_dict(
            orient="records"
        )

        enriched_pdf = generate_latent_dataframe_pandas(
            filtered,
            checkpoint_dir="utils/model/vehicle_autoencoders",
            device="cpu"
        )

        norm_summary = compute_grid_normalisation(
            enriched_pdf,
            grid_size=0.2,
        )

        autoencoder_pivot = norm_summary.pivot_table(
            index="TIME_PERIOD",
            columns="Motor energy",
            values="normalized_registrations",
            fill_value=0
        ).reset_index()

        if not autoencoder_pivot.empty:
            autoencoder_pivot.rename(
                columns={"TIME_PERIOD": "year"},
                inplace=True
            )

            autoencoder_chart_data = (
                autoencoder_pivot.to_dict(
                    orient="records"
                )
            )
        else:
            autoencoder_chart_data = []

        series_config = get_motor_energy_colors()

        return (
            raw_chart_data,
            baseline_chart_data,
            autoencoder_chart_data,
            series_config
        )
    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack, dmc.Stack]:
        _, _, _, series_config = self._get_chart_payload([self.min_year, self.max_year], self.default_geo)
        
        content = self.view.render_content([], series_config)
        filters_desktop = self.view.render_filters(self.min_year, self.max_year, self.geo_options, self.default_geo, suffix="desktop")
        filters_mobile = self.view.render_filters(self.min_year, self.max_year, self.geo_options, self.default_geo, suffix="mobile")

        return content, filters_desktop, filters_mobile

    def _register_callbacks(self):
        @callback(
            Output("overview-timeseries-raw-chart", "data"),
            Output("overview-timeseries-baseline-chart", "data"),
            Output("overview-timeseries-autoencoder-chart", "data"),
            Output("overview-year-slider-desktop", "value"),
            Output("overview-year-slider-mobile", "value"),
            Output("overview-geo-select-desktop", "value"),
            Output("overview-geo-select-mobile", "value"),
            Input("overview-year-slider-desktop", "value"),
            Input("overview-year-slider-mobile", "value"),
            Input("overview-geo-select-desktop", "value"),
            Input("overview-geo-select-mobile", "value"),
            prevent_initial_call=True
        )
        def update_chart(year_d, year_m, geo_d, geo_m):
            trigger = ctx.triggered_id

            if trigger == "overview-year-slider-desktop":
                active_years, active_geo = year_d, geo_d
                out_year_d, out_year_m = dash.no_update, year_d
                out_geo_d, out_geo_m = dash.no_update, dash.no_update
            elif trigger == "overview-year-slider-mobile":
                active_years, active_geo = year_m, geo_m
                out_year_d, out_year_m = year_m, dash.no_update
                out_geo_d, out_geo_m = dash.no_update, dash.no_update
            elif trigger == "overview-geo-select-desktop":
                active_years, active_geo = year_d, geo_d
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_geo_d, out_geo_m = dash.no_update, geo_d
            elif trigger == "overview-geo-select-mobile":
                active_years, active_geo = year_m, geo_m
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_geo_d, out_geo_m = geo_m, dash.no_update
            else:
                return [dash.no_update] * 7

            if not active_years or not active_geo:
                return [dash.no_update] * 7

            raw_chart_data, baseline_chart_data, autoencoder_chart_data, _ = self._get_chart_payload(active_years, active_geo)

            raw_chart_data = round_data_to_two_decimals(raw_chart_data)
            baseline_chart_data = round_data_to_two_decimals(baseline_chart_data)
            autoencoder_chart_data = round_data_to_two_decimals(autoencoder_chart_data)

            return (
                raw_chart_data,
                baseline_chart_data,
                autoencoder_chart_data,
                out_year_d,
                out_year_m,
                out_geo_d,
                out_geo_m
            )

        @callback(
            Output("overview-timeseries-raw-chart", "series"),
            Output("overview-timeseries-baseline-chart", "series"),
            Output("overview-timeseries-autoencoder-chart", "series"),
            Input("overview-series-filter", "value"),
            prevent_initial_call=True
        )
        def sync_chart_series(selected_series_names):
            if not selected_series_names:
                filtered_series = []
            else:
                # 
                filtered_series = [
                    s for s in get_motor_energy_colors() 
                    if s["name"] in selected_series_names
                ]
                
            return filtered_series, filtered_series, filtered_series