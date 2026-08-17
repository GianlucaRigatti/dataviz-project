import dash
from dash import Input, Output, State, callback, ctx, clientside_callback
import dash_mantine_components as dmc

from utils.data_loader import (
    extract_baseline_factors,
    compute_latent_volumes,
    generate_latent_dataframe_pandas,
    get_dataframe,
    get_motor_energy_colors,
    get_motor_energy_plotly_colors,
    round_data_to_two_decimals,
)

from views.volume_view import VolumeView
import pandas as pd
import plotly.graph_objects as go

class VolumeController:
    def __init__(self):
        self.view = VolumeView()
        self._load_data()
        self._register_callbacks()

    def _load_data(self):
        self.df = get_dataframe()
        self.min_year = int(self.df["TIME_PERIOD"].min())
        self.max_year = int(self.df["TIME_PERIOD"].max())

        geo_df = self.df[~self.df["geo"].isin(["EU27_2020", "EU28", "EU"])][
            [
                "geo",
                "Geopolitical entity (reporting)"
            ]
        ].drop_duplicates()

        self.geo_options = [
            {"value": row["geo"], "label": row["Geopolitical entity (reporting)"]}
            for _, row in geo_df.iterrows()
        ]
        self.geo_options.sort(key=lambda x: x["label"])
        self.geo_options.insert(0, {"value": "EU27_2020", "label": "European Union (EU27)"})
        self.default_geo = "EU27_2020"

        self.latent_df = generate_latent_dataframe_pandas(
            self.df,
            checkpoint_dir="utils/model/vehicle_autoencoder",
            device="cpu",
        )

    def _get_manufacturer_table_data(self, years: list[int], region: str) -> list[dict]:

        if not years or not region:
            return []

        min_y, max_y = years

        if region == "EU27_2020":
            filtered = self.df[
                self.df["TIME_PERIOD"].between(min_y, max_y)
            ].copy()
        else:
            filtered = self.df[
                (self.df["geo"] == region)
                & self.df["TIME_PERIOD"].between(min_y, max_y)
            ].copy()

        if filtered.empty:
            return []

        manufacturer_df = filtered[
            [
                "TIME_PERIOD",
                "manufacturer_name_eu_standard_denomination",
                "registrations",
            ]
        ].copy()

        manufacturer_df["registrations"] = pd.to_numeric(
            manufacturer_df["registrations"],
            errors="coerce",
        )

        manufacturer_df = manufacturer_df.dropna(
            subset=[
                "TIME_PERIOD",
                "manufacturer_name_eu_standard_denomination",
                "registrations",
            ]
        )

        manufacturer_df[
            "manufacturer_name_eu_standard_denomination"
        ] = (
            manufacturer_df[
                "manufacturer_name_eu_standard_denomination"
            ]
            .astype(str)
            .str.strip()
        )

        manufacturer_df = manufacturer_df[
            manufacturer_df[
                "manufacturer_name_eu_standard_denomination"
            ] != ""
        ]

        if manufacturer_df.empty:
            return []

        # Aggregate registrations by year and manufacturer
        manufacturer_totals = (
            manufacturer_df
            .groupby(
                [
                    "TIME_PERIOD",
                    "manufacturer_name_eu_standard_denomination",
                ],
                as_index=False,
            )
            .agg(
                registrations=("registrations", "sum")
            )
        )

        # Sort manufacturers within each year
        manufacturer_totals = manufacturer_totals.sort_values(
            [
                "TIME_PERIOD",
                "registrations",
                "manufacturer_name_eu_standard_denomination",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )

        # Keep the top 3 manufacturers for each year
        top_three = (
            manufacturer_totals
            .groupby("TIME_PERIOD", sort=True)
            .head(3)
        )

        result = []
        for year, year_df in top_three.groupby(
            "TIME_PERIOD",
            sort=True,
        ):
            top_manufacturers = [
                (
                    row[
                        "manufacturer_name_eu_standard_denomination"
                    ],
                    int(row["registrations"]),
                )
                for _, row in year_df.iterrows()
            ]

            result.append(
                {
                    "year": int(year),
                    "top_manufacturers": top_manufacturers,
                }
            )
        return result

    def _get_latent_scatter_figure(self, years: list[int], region: str, scatter_year: int | str, theme: str = "light") -> go.Figure:
        if not years or not region:
            return go.Figure()

        min_y, max_y = years
        scatter_year = int(scatter_year)

        if region == "EU27_2020":
            filtered = self.latent_df[
                (self.latent_df["TIME_PERIOD"] >= min_y)
                & (self.latent_df["TIME_PERIOD"] <= max_y)
            ]
        else:
            filtered = self.latent_df[
                (self.latent_df["geo"] == region)
                & (self.latent_df["TIME_PERIOD"] >= min_y)
                & (self.latent_df["TIME_PERIOD"] <= max_y)
            ]

        if filtered.empty:
            return go.Figure()

        points = filtered[
            filtered["TIME_PERIOD"] == scatter_year
        ].copy()

        if points.empty:
            return go.Figure()


        fig = go.Figure()
        color_map = get_motor_energy_plotly_colors()

        for series in get_motor_energy_colors():

            motor_energy = series["name"]

            energy_points = points[
                points["Motor energy"] == motor_energy
            ]

            if energy_points.empty:
                continue

            color = color_map.get(
                motor_energy,
                "#868E96",
            )

            fig.add_trace(
                go.Scattergl(
                    x=energy_points["z_1"],
                    y=energy_points["z_2"],
                    mode="markers",
                    name=motor_energy,
                    marker={
                        "color": color,
                        "size": 8,
                        "opacity": 0.6,
                    },
                    customdata=energy_points[
                        [
                            "TIME_PERIOD",
                            "registrations",
                            "manufacturer_name_eu_standard_denomination",
                            "commercial_name",
                        ]
                    ].values,
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Year: %{customdata[0]}<br>"
                        "Registrations: %{customdata[1]:,}<br>"
                        "Manufacturer: %{customdata[2]}<br>"
                        "Model: %{customdata[3]}<br>"
                        "Latent X: %{x:.2f}<br>"
                        "Latent Y: %{y:.2f}"
                        "<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            template=(
                "mantine_dark"
                if theme == "dark"
                else "mantine_light"
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={
                "title": "Latent Dimension 1",
                "zeroline": False,
            },
            yaxis={
                "title": "Latent Dimension 2",
                "zeroline": False,
            },
            showlegend=False,
        )

        return fig

    def _get_chart_payload(self, years: list[int], region: str) -> tuple[list[dict], list[dict], list[dict]]:
        if not years or not region:
            return [], [], [], []

        min_y, max_y = years

        if region == "EU27_2020":
            filtered = self.df[(self.df["TIME_PERIOD"] >= min_y) & (self.df["TIME_PERIOD"] <= max_y)]
        else:
            filtered = self.df[(self.df["geo"] == region) & (self.df["TIME_PERIOD"] >= min_y) & (self.df["TIME_PERIOD"] <= max_y)]

        if filtered.empty:
            return [], [], [], []

        baseline_factors = extract_baseline_factors(filtered)

        baseline_wide = (
            baseline_factors
            .pivot_table(
                index="TIME_PERIOD",
                columns="Motor energy",
                values="unique_choices",
                aggfunc="first",
            )
            .reset_index()
        )

        baseline_wide.rename(
            columns={
                "TIME_PERIOD": "year"
            },
            inplace=True,
        )

        baseline_factors_data = (
            baseline_wide.to_dict(
                orient="records"
            )
        )

        if region == "EU27_2020":
            latent_filtered = self.latent_df[(self.latent_df["TIME_PERIOD"] >= min_y) & (self.latent_df["TIME_PERIOD"] <= max_y)]
        else:
            latent_filtered = self.latent_df[(self.latent_df["geo"] == region) & (self.latent_df["TIME_PERIOD"] >= min_y) & (self.latent_df["TIME_PERIOD"] <= max_y)]

        latent_normalization_data = compute_latent_volumes(latent_filtered, grid_size=0.2)

        if latent_normalization_data:
            latent_df = pd.DataFrame(latent_normalization_data)

            latent_wide = (
                latent_df
                .pivot_table(
                    index="TIME_PERIOD",
                    columns="Motor energy",
                    values="normalized_registrations",
                    aggfunc="first",
                )
                .reset_index()
            )

            latent_wide.rename(
                columns={
                    "TIME_PERIOD": "year"
                },
                inplace=True,
            )

            all_years = pd.DataFrame({"year": range(min_y, max_y + 1)})
            latent_wide = all_years.merge(
                latent_wide,
                on="year",
                how="left",
            )
            latent_wide = latent_wide.sort_values(
                "year"
            )
            latent_normalization_chart_data = (
                latent_wide.to_dict(
                    orient="records"
                )
            )

        else:
            latent_normalization_chart_data = []

        manufacturer_table_data = self._get_manufacturer_table_data(years, region)

        return (
            baseline_factors_data,
            latent_normalization_chart_data,
            manufacturer_table_data
        )

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack, dmc.Stack]:

        series_config = get_motor_energy_colors()
        content = self.view.render_content(
            initial_factors_data=[],
            initial_latent_data=[],
            initial_manufacturer_table_data=[],
            initial_latent_scatter_figure=go.Figure(),
            series_config=series_config,
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

        return (
            content,
            filters_desktop,
            filters_mobile,
        )

    def _register_callbacks(self):

        clientside_callback(
            """
            function(loadingState) {
                return Boolean(
                    loadingState &&
                    loadingState.is_loading
                );
            }
            """,
            Output("volume-latent-scatter-loading-overlay", "visible"),
            Input("volume-latent-scatter-chart", "loading_state"),
        )

        @callback(
            Output("volume-scatter-year-select", "data"),
            Output("volume-scatter-year-select", "value"),
            Input("volume-year-slider-desktop", "value"),
            State("volume-scatter-year-select", "value"),
        )
        def update_scatter_year_options(slider_range, current_select_value):
            if not slider_range:
                return [], None

            start_year, end_year = slider_range

            options = [
                {
                    "label": str(year),
                    "value": str(year),
                }
                for year in range(
                    start_year,
                    end_year + 1,
                )
            ]

            if current_select_value is None:
                new_value = str(end_year)
            else:
                try:
                    current_year = int(current_select_value)
                except (TypeError, ValueError):
                    current_year = end_year

                current_year = max(
                    start_year,
                    min(end_year, current_year),
                )

                new_value = str(current_year)

            return options, new_value

        @callback(
            Output("volume-latent-scatter-chart", "figure", allow_duplicate=True),
            Input("volume-scatter-filter", "value"),
            State("volume-latent-scatter-chart", "figure"),
            running=[(Output("volume-latent-scatter-loading-overlay", "visible"), True, False)],
            prevent_initial_call=True,
        )
        def update_scatter_visibility(selected_series, figure):
            if not figure:
                return dash.no_update

            selected_series = set(selected_series or [])

            for trace in figure["data"]:
                trace["visible"] = (
                    trace.get("name") in selected_series
                )

            return figure

        @callback(
            Output("volume-latent-scatter-chart", "figure"),
            Input("volume-year-slider-desktop", "value"),
            Input("volume-geo-select-desktop", "value"),
            Input("volume-scatter-year-select", "value"),
            Input("color-scheme-switch", "computedColorScheme"),
            running=[(Output("volume-latent-scatter-loading-overlay", "visible"), True, False)],
        )
        def update_scatter(years, region, scatter_selected_year, theme_state):
            if not years or not region:
                return go.Figure()

            min_y, max_y = years

            if scatter_selected_year is None:
                scatter_year = max_y
            else:
                try:
                    scatter_year = int(scatter_selected_year)
                except (TypeError, ValueError):
                    scatter_year = max_y

            scatter_year = max(
                min_y,
                min(max_y, scatter_year),
            )

            theme = (
                "dark"
                if theme_state == "dark"
                else "light"
            )

            return self._get_latent_scatter_figure(
                years=years,
                region=region,
                scatter_year=scatter_year,
                theme=theme,
            )

        @callback(
            Output("volume-timeseries-factors-chart", "data"),
            Output("volume-timeseries-latent-volume-chart", "data"),
            Output("volume-manufacturer-table", "children"),
            Output("volume-year-slider-desktop", "value"),
            Output("volume-year-slider-mobile", "value"),
            Output("volume-geo-select-desktop", "value"),
            Output("volume-geo-select-mobile", "value"),
            Input("volume-year-slider-desktop", "value"),
            Input("volume-year-slider-mobile", "value"),
            Input("volume-geo-select-desktop", "value"),
            Input("volume-geo-select-mobile", "value"),
        )
        def update_chart(year_d, year_m, geo_d, geo_m):
            trigger = ctx.triggered_id

            # Initial page load
            if trigger is None:
                active_years = year_d
                active_geo = geo_d

                out_year_d = dash.no_update
                out_year_m = dash.no_update
                out_geo_d = dash.no_update
                out_geo_m = dash.no_update

            elif trigger == "volume-year-slider-desktop":
                active_years = year_d
                active_geo = geo_d

                out_year_d = dash.no_update
                out_year_m = year_d

                out_geo_d = dash.no_update
                out_geo_m = dash.no_update

            elif trigger == "volume-year-slider-mobile":
                active_years = year_m
                active_geo = geo_m

                out_year_d = year_m
                out_year_m = dash.no_update

                out_geo_d = dash.no_update
                out_geo_m = dash.no_update

            elif trigger == "volume-geo-select-desktop":
                active_years = year_d
                active_geo = geo_d

                out_year_d = dash.no_update
                out_year_m = dash.no_update

                out_geo_d = dash.no_update
                out_geo_m = geo_d

            elif trigger == "volume-geo-select-mobile":
                active_years = year_m
                active_geo = geo_m

                out_year_d = dash.no_update
                out_year_m = dash.no_update

                out_geo_d = geo_m
                out_geo_m = dash.no_update

            else:
                return [dash.no_update] * 7

            if not active_years or not active_geo:
                return [dash.no_update] * 7

            (
                baseline_factors_data,
                latent_volume_data,
                manufacturer_table_data,
            ) = self._get_chart_payload(
                active_years,
                active_geo,
            )

            baseline_factors_data = round_data_to_two_decimals(
                baseline_factors_data
            )

            latent_volume_data = round_data_to_two_decimals(
                latent_volume_data
            )

            manufacturer_table = (
                self.view.render_manufacturer_table(
                    manufacturer_table_data
                )
            )

            return (
                baseline_factors_data,
                latent_volume_data,
                manufacturer_table,
                out_year_d,
                out_year_m,
                out_geo_d,
                out_geo_m,
            )

        @callback(
            Output("volume-timeseries-factors-chart", "series"),
            Output("volume-timeseries-latent-volume-chart", "series"),
            Input("volume-series-filter", "value"),
            prevent_initial_call=True,
        )
        def sync_chart_series(selected_series_names):
            if not selected_series_names:
                return [], []

            filtered_series = [
                s for s in get_motor_energy_colors()
                if s["name"] in selected_series_names
            ]

            return (
                filtered_series,
                filtered_series,
            )