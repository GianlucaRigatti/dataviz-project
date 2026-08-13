import dash
from dash import Input, Output, callback, ctx
import dash_mantine_components as dmc
from utils.data_loader import extract_baseline_factors, extract_latent_volume_bubbles, generate_latent_dataframe_pandas, get_dataframe, get_motor_energy_colors, round_data_to_two_decimals
from views.volume_view import VolumeView


class VolumeController:
    def __init__(self):
        self.view = VolumeView()
        self._load_data()
        self._register_callbacks()

    def _load_data(self):
        self.df = get_dataframe()

        self.min_year = int(self.df["TIME_PERIOD"].min())
        self.max_year = int(self.df["TIME_PERIOD"].max())

        geo_df = self.df[
            ~self.df["geo"].isin(["EU27_2020", "EU28", "EU"])
        ][
            ["geo", "Geopolitical entity (reporting)"]
        ].drop_duplicates()

        self.geo_options = [
            {
                "value": row["geo"],
                "label": row["Geopolitical entity (reporting)"],
            }
            for _, row in geo_df.iterrows()
        ]

        self.geo_options.sort(key=lambda x: x["label"])
        self.geo_options.insert(
            0,
            {
                "value": "EU27_2020",
                "label": "European Union (EU27)",
            },
        )

        self.default_geo = "EU27_2020"
        self.latent_df = generate_latent_dataframe_pandas(self.df)

    def _get_chart_payload(
        self,
        years: list[int],
        region: str,
    ) -> tuple[list[dict], list[dict], list[dict]]:

        if not years or not region:
            return [], [], []

        min_y, max_y = years

        if region == "EU27_2020":
            filtered = self.df[
                (self.df["TIME_PERIOD"] >= min_y)
                & (self.df["TIME_PERIOD"] <= max_y)
            ]
        else:
            filtered = self.df[
                (self.df["geo"] == region)
                & (self.df["TIME_PERIOD"] >= min_y)
                & (self.df["TIME_PERIOD"] <= max_y)
            ]

        if filtered.empty:
            return [], [], []

        baseline_factors = extract_baseline_factors(filtered)

        wide_df = baseline_factors.pivot(
            index="TIME_PERIOD",
            columns="Motor energy",
            values="unique_choices",
        ).reset_index()

        baseline_factors_data = wide_df.to_dict(
            orient="records"
        )

        if region == "EU27_2020":
            latent_filtered = self.latent_df[
                (self.latent_df["TIME_PERIOD"] >= min_y)
                & (self.latent_df["TIME_PERIOD"] <= max_y)
            ]
        else:
            latent_filtered = self.latent_df[
                (self.latent_df["geo"] == region)
                & (self.latent_df["TIME_PERIOD"] >= min_y)
                & (self.latent_df["TIME_PERIOD"] <= max_y)
            ]

        bubble_data = extract_latent_volume_bubbles(
            latent_filtered
        )

        series_config = get_motor_energy_colors()

        return (
            baseline_factors_data,
            bubble_data,
            series_config,
        )

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack, dmc.Stack]:
        (
            baseline_factors_data,
            bubble_data,
            series_config,
        ) = self._get_chart_payload(
            [self.min_year, self.max_year], self.default_geo
        )

        content = self.view.render_content(
            baseline_factors_data, bubble_data, series_config
        )
        filters_desktop = self.view.render_filters(
            self.min_year,
            self.max_year,
            self.geo_options,
            self.default_geo,
            suffix="desktop",
        )
        filters_mobile = self.view.render_filters(
            self.min_year,
            self.max_year,
            self.geo_options,
            self.default_geo,
            suffix="mobile",
        )

        return content, filters_desktop, filters_mobile

    def _register_callbacks(self):

        @callback(
            Output("volume-timeseries-factors-chart", "data"),
            Output("volume-energy-bubble-chart", "data"),
            Output("volume-year-slider-desktop", "value"),
            Output("volume-year-slider-mobile", "value"),
            Output("volume-geo-select-desktop", "value"),
            Output("volume-geo-select-mobile", "value"),
            Input("volume-year-slider-desktop", "value"),
            Input("volume-year-slider-mobile", "value"),
            Input("volume-geo-select-desktop", "value"),
            Input("volume-geo-select-mobile", "value"),
            prevent_initial_call=True,
        )
        def update_chart(year_d, year_m, geo_d, geo_m):
            trigger = ctx.triggered_id

            if trigger == "volume-year-slider-desktop":
                active_years, active_geo = year_d, geo_d
                out_year_d, out_year_m = dash.no_update, year_d
                out_geo_d, out_geo_m = dash.no_update, dash.no_update
            elif trigger == "volume-year-slider-mobile":
                active_years, active_geo = year_m, geo_m
                out_year_d, out_year_m = year_m, dash.no_update
                out_geo_d, out_geo_m = dash.no_update, dash.no_update
            elif trigger == "volume-geo-select-desktop":
                active_years, active_geo = year_d, geo_d
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_geo_d, out_geo_m = dash.no_update, geo_d
            elif trigger == "volume-geo-select-mobile":
                active_years, active_geo = year_m, geo_m
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_geo_d, out_geo_m = geo_m, dash.no_update
            else:
                return [dash.no_update] * 6

            if not active_years or not active_geo:
                return [dash.no_update] * 6

            (
                baseline_factors_data,
                bubble_data,
                _,
            ) = self._get_chart_payload(active_years, active_geo)
            baseline_factors_data = round_data_to_two_decimals(
                baseline_factors_data
            )

            return (
                baseline_factors_data,
                bubble_data,
                out_year_d,
                out_year_m,
                out_geo_d,
                out_geo_m,
            )

        @callback(
            Output("volume-timeseries-factors-chart", "series"),
            Input("volume-series-filter", "value"),
            prevent_initial_call=True,
        )
        def sync_chart_series(selected_series_names):
            if not selected_series_names:
                return []

            return [
                s
                for s in get_motor_energy_colors()
                if s["name"] in selected_series_names
            ]