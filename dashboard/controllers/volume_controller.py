import dash
from dash import Input, Output, callback, ctx
import dash_mantine_components as dmc

from utils.data_loader import (
    extract_baseline_factors,
    compute_latent_volumes,
    generate_latent_dataframe_pandas,
    get_dataframe,
    get_motor_energy_colors,
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

        self.min_year = int(
            self.df["TIME_PERIOD"].min()
        )

        self.max_year = int(
            self.df["TIME_PERIOD"].max()
        )

        geo_df = self.df[
            ~self.df["geo"].isin(
                ["EU27_2020", "EU28", "EU"]
            )
        ][
            [
                "geo",
                "Geopolitical entity (reporting)"
            ]
        ].drop_duplicates()

        self.geo_options = [
            {
                "value": row["geo"],
                "label": row[
                    "Geopolitical entity (reporting)"
                ],
            }
            for _, row in geo_df.iterrows()
        ]

        self.geo_options.sort(
            key=lambda x: x["label"]
        )

        self.geo_options.insert(
            0,
            {
                "value": "EU27_2020",
                "label": "European Union (EU27)",
            },
        )

        self.default_geo = "EU27_2020"

        self.latent_df = generate_latent_dataframe_pandas(
            self.df,
            checkpoint_dir="utils/model/vehicle_autoencoder",
            device="cpu",
        )

    def _get_manufacturer_table_data(
        self,
        years: list[int],
        region: str,
    ) -> list[dict]:

        if not years or not region:
            return []

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

        manufacturer_df = manufacturer_df[
            manufacturer_df[
                "manufacturer_name_eu_standard_denomination"
            ].astype(str).str.strip() != ""
        ]

        if manufacturer_df.empty:
            return []

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

        winners = (
            manufacturer_totals
            .drop_duplicates(
                subset=["TIME_PERIOD"],
                keep="first",
            )
            .sort_values("TIME_PERIOD")
        )

        return [
            {
                "year": int(row["TIME_PERIOD"]),
                "manufacturer": row[
                    "manufacturer_name_eu_standard_denomination"
                ],
                "registrations": int(row["registrations"]),
            }
            for _, row in winners.iterrows()
        ]

    def _get_latent_scatter_figure(
        self,
        years: list[int],
        region: str,
    ) -> go.Figure:

        if not years or not region:
            return go.Figure()

        min_y, max_y = years

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

        fig = go.Figure()

        for series in get_motor_energy_colors():

            motor_energy = series["name"]

            points = filtered[
                (filtered["Motor energy"] == motor_energy) &
                (filtered["TIME_PERIOD"] == max_y)
            ]

            if points.empty:
                continue

            color_map = {
                "red.6": "#fa5252",
                "blue.6": "#4dabf7",
                "teal.6": "#20c997",
                "orange.6": "#fd7e14",
                "cyan.6": "#15aabf",
                "gray.6": "#868e96",
            }

            color = color_map.get(
                series["color"],
                "#868e96",
            )

            fig.add_trace(
                go.Scattergl(
                    x=points["z_1"],
                    y=points["z_2"],
                    mode="markers",
                    name=motor_energy,
                    marker={
                        "color": color,
                        "size": 5,
                        "opacity": 0.55,
                    },
                    customdata=points[
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
            template="plotly_dark",
            height=500,
            margin={
                "l": 20,
                "r": 20,
                "t": 20,
                "b": 20,
            },
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
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )

        return fig

    def _get_chart_payload(
        self,
        years: list[int],
        region: str,
    ) -> tuple[list[dict], list[dict], list[dict], go.Figure, list[dict]]:

        if not years or not region:
            return [], [], [], []

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
            return [], [], [], []

        baseline_factors = extract_baseline_factors(
            filtered
        )

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

        latent_normalization_data = compute_latent_volumes(
            latent_filtered,
            grid_size=0.2,
        )

        if latent_normalization_data:

            latent_df = pd.DataFrame(
                latent_normalization_data
            )

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

            all_years = pd.DataFrame(
                {
                    "year": range(
                        min_y,
                        max_y + 1,
                    )
                }
            )

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

        manufacturer_table_data = self._get_manufacturer_table_data(
            years,
            region,
        )

        latent_scatter_figure = self._get_latent_scatter_figure(
            years,
            region,
        )

        series_config = get_motor_energy_colors()

        return (
            baseline_factors_data,
            latent_normalization_chart_data,
            manufacturer_table_data,
            latent_scatter_figure,
            series_config,
        )

    def get_layouts(
        self
    ) -> tuple[dmc.Stack, dmc.Stack, dmc.Stack]:

        (
            baseline_factors_data,
            latent_volume_data,
            manufacturer_table_data,
            latent_scatter_figure,
            series_config,
        ) = self._get_chart_payload(
            [self.min_year, self.max_year],
            self.default_geo,
        )

        content = self.view.render_content(
            baseline_factors_data,
            latent_volume_data,
            manufacturer_table_data,
            latent_scatter_figure,
            series_config,
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

        @callback(
            Output(
                "volume-timeseries-factors-chart",
                "data",
            ),
            Output(
                "volume-timeseries-latent-volume-chart",
                "data",
            ),
            Output(
                "volume-manufacturer-table",
                "children",
            ),
            Output(
                "volume-latent-scatter-chart",
                "figure",
            ),
            Output(
                "volume-year-slider-desktop",
                "value",
            ),
            Output(
                "volume-year-slider-mobile",
                "value",
            ),
            Output(
                "volume-geo-select-desktop",
                "value",
            ),
            Output(
                "volume-geo-select-mobile",
                "value",
            ),
            Input(
                "volume-year-slider-desktop",
                "value",
            ),
            Input(
                "volume-year-slider-mobile",
                "value",
            ),
            Input(
                "volume-geo-select-desktop",
                "value",
            ),
            Input(
                "volume-geo-select-mobile",
                "value",
            ),
            prevent_initial_call=True,
        )
        def update_chart(
            year_d,
            year_m,
            geo_d,
            geo_m,
        ):

            trigger = ctx.triggered_id

            if trigger == "volume-year-slider-desktop":

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
                return [dash.no_update] * 8

            if not active_years or not active_geo:
                return [dash.no_update] * 8

            (
                baseline_factors_data,
                latent_volume_data,
                manufacturer_table_data,
                latent_scatter_figure,
                _,
            ) = self._get_chart_payload(
                active_years,
                active_geo,
            )

            baseline_factors_data = (
                round_data_to_two_decimals(
                    baseline_factors_data
                )
            )

            manufacturer_table = self.view.render_manufacturer_table(
                manufacturer_table_data
            )

            latent_volume_data = (
                round_data_to_two_decimals(
                    latent_volume_data
                )
            )

            return (
                baseline_factors_data,
                latent_volume_data,
                manufacturer_table,
                latent_scatter_figure,
                out_year_d,
                out_year_m,
                out_geo_d,
                out_geo_m,
            )

        @callback(
            Output(
                "volume-timeseries-factors-chart",
                "series",
            ),
            Output(
                "volume-timeseries-latent-volume-chart",
                "series",
            ),
            Input(
                "volume-series-filter",
                "value",
            ),
            prevent_initial_call=True,
        )
        def sync_chart_series(
            selected_series_names
        ):

            if not selected_series_names:
                return [], []

            filtered_series = [
                s
                for s in get_motor_energy_colors()
                if s["name"] in selected_series_names
            ]

            return (
                filtered_series,
                filtered_series,
            )