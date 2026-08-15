import dash
from dash import callback, ctx, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.express as px
import numpy as np
import pandas as pd

from views.geo_view import GeoView
from utils.data_loader import (
    get_dataframe,
    extract_baseline_factors,
    compute_baseline_normalization,
    generate_latent_dataframe_pandas,
    compute_grid_normalisation,
)


class GeoController:
    def __init__(self):
        dmc.add_figure_templates()

        self.view = GeoView()

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

        self.geo_df = self.df[
            ~self.df["geo"].isin(
                [
                    "EU27_2020",
                    "EU28",
                    "EU",
                ]
            )
        ].copy()

        import pycountry

        def get_iso3(iso2):
            mapping = {
                "UK": "GB",
                "EL": "GR",
            }

            iso2 = mapping.get(iso2, iso2)

            country = pycountry.countries.get(
                alpha_2=iso2
            )

            if country is None:
                return None

            return country.alpha_3

        self.geo_df["iso3"] = (
            self.geo_df["geo"]
            .apply(get_iso3)
        )

        self.geo_df = self.geo_df.dropna(
            subset=["iso3"]
        )

        energies = (
            self.geo_df["Motor energy"]
            .dropna()
            .unique()
        )

        self.energy_options = [
            {
                "value": energy,
                "label": energy,
            }
            for energy in energies
        ]

        self.energy_options.sort(
            key=lambda x: x["label"]
        )

        self.default_energy = (
            self.energy_options[0]["value"]
            if self.energy_options
            else None
        )

    def _calculate_country_normalization(
        self,
        country_df: pd.DataFrame,
        metric: str,
    ) -> pd.DataFrame:

        if country_df.empty:
            return pd.DataFrame(
                columns=[
                    "TIME_PERIOD",
                    "Motor energy",
                    "normalized_value",
                ]
            )

        if metric == "baseline":
            baseline_factors = extract_baseline_factors(
                country_df
            )

            baseline_summary = compute_baseline_normalization(
                country_df,
                factors_df=baseline_factors,
            )

            if baseline_summary.empty:
                return pd.DataFrame(
                    columns=[
                        "TIME_PERIOD",
                        "Motor energy",
                        "normalized_value",
                    ]
                )

            result = baseline_summary[
                [
                    "TIME_PERIOD",
                    "Motor energy",
                    "baseline_normalized_registrations",
                ]
            ].copy()

            result = result.rename(
                columns={
                    "baseline_normalized_registrations":
                        "normalized_value"
                }
            )

            return result

        if metric == "autoencoder":
            enriched_pdf = generate_latent_dataframe_pandas(
                country_df,
                checkpoint_dir="utils/model/vehicle_autoencoder",
                device="cpu",
            )

            norm_summary = compute_grid_normalisation(
                enriched_pdf,
                grid_size=0.2,
            )

            if norm_summary.empty:
                return pd.DataFrame(
                    columns=[
                        "TIME_PERIOD",
                        "Motor energy",
                        "normalized_value",
                    ]
                )

            result = norm_summary[
                [
                    "TIME_PERIOD",
                    "Motor energy",
                    "normalized_registrations",
                ]
            ].copy()

            result = result.rename(
                columns={
                    "normalized_registrations":
                        "normalized_value"
                }
            )

            return result

        return pd.DataFrame(
            columns=[
                "TIME_PERIOD",
                "Motor energy",
                "normalized_value",
            ]
        )

    def _get_choropleth(
        self,
        year_range,
        energy: list[str],
        metric: str = "raw",
        theme: str = "light",
    ):
        if not year_range or not energy:
            return {}

        if isinstance(year_range, (list, tuple)):
            start_year = int(year_range[0])
            end_year = int(year_range[-1])
        else:
            start_year = int(year_range)
            end_year = int(year_range)

        if start_year > end_year:
            start_year, end_year = end_year, start_year

        range_df = self.geo_df[
            self.geo_df["TIME_PERIOD"].between(
                start_year,
                end_year,
            )
        ].copy()

        if range_df.empty:
            return {}

        if metric == "raw":
            filtered = range_df[
                range_df["Motor energy"].isin(energy)
            ].copy()

            if filtered.empty:
                return {}

            country_data = (
                filtered
                .groupby(
                    [
                        "iso3",
                        "Geopolitical entity (reporting)",
                    ],
                    as_index=False,
                )
                .agg(
                    registrations=(
                        "registrations",
                        "sum",
                    )
                )
            )

            val_col = "registrations"
            hover_label = "Registrations"

        else:
            hover_label = (
                "Baseline Normalized"
                if metric == "baseline"
                else "Autoencoder Normalized"
            )

            country_results = []

            for (
                iso3,
                country_name,
            ), country_group in range_df.groupby(
                [
                    "iso3",
                    "Geopolitical entity (reporting)",
                ],
                sort=False,
            ):
                if country_group.empty:
                    continue

                normalized = self._calculate_country_normalization(
                    country_group,
                    metric,
                )

                if normalized.empty:
                    continue

                normalized = normalized[
                    normalized["Motor energy"].isin(energy)
                ].copy()

                if normalized.empty:
                    continue

                normalized["normalized_value"] = pd.to_numeric(
                    normalized["normalized_value"],
                    errors="coerce",
                )

                total_value = normalized[
                    "normalized_value"
                ].sum(
                    min_count=1
                )

                country_results.append(
                    {
                        "iso3": iso3,
                        "Geopolitical entity (reporting)":
                            country_name,
                        "normalized_value":
                            total_value,
                    }
                )

            if not country_results:
                return {}

            country_data = pd.DataFrame(
                country_results
            )

            val_col = "normalized_value"

        country_data["display_value"] = pd.to_numeric(
            country_data[val_col],
            errors="coerce",
        )

        color_values = (
            country_data["display_value"]
            .fillna(0)
            .clip(lower=1)
        )

        country_data["log_val"] = np.log10(
            color_values
        )

        fig = px.choropleth(
            country_data,
            locations="iso3",
            locationmode="ISO-3",
            color="log_val",
            hover_name="Geopolitical entity (reporting)",
            color_continuous_scale="Blues",
            labels={
                "log_val": hover_label,
            },
            projection="natural earth",
        )

        num_format = (
            ",.0f"
            if metric == "raw"
            else ",.2f"
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b>"
                f"<br>{hover_label}: "
                f"%{{customdata:{num_format}}}"
                "<extra></extra>"
            ),
            customdata=country_data[
                ["display_value"]
            ],
        )

        fig.update_geos(
            fitbounds="locations",
            showland=True,
            showframe=False,
            showocean=True,
            showcountries=True,
            showcoastlines=True,
        )

        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0,
            ),
            template=(
                "mantine_dark"
                if theme == "dark"
                else "mantine_light"
            ),
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig

    def get_layouts(self):
        content = self.view.render_content(
            self.min_year,
            self.max_year,
        )

        filters_desktop = self.view.render_filters(
            self.energy_options,
            self.default_energy,
            suffix="desktop",
        )

        filters_mobile = self.view.render_filters(
            self.energy_options,
            self.default_energy,
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
                "geo-map-chart",
                "figure",
            ),
            Output(
                "geo-energy-select-desktop",
                "value",
            ),
            Output(
                "geo-energy-select-mobile",
                "value",
            ),
            Input(
                "geo-year-slider",
                "value",
            ),
            Input(
                "geo-metric-select",
                "value",
            ),
            Input(
                "geo-energy-select-desktop",
                "value",
            ),
            Input(
                "geo-energy-select-mobile",
                "value",
            ),
            Input(
                "color-scheme-switch",
                "computedColorScheme",
            ),
        )
        def update_map(
            year,
            metric,
            energy_d,
            energy_m,
            theme_state,
        ):
            trigger = ctx.triggered_id

            current_theme = (
                "dark"
                if theme_state == "dark"
                else "light"
            )

            active_energy = (
                energy_d
                if energy_d
                else energy_m
            )

            out_energy_d = dash.no_update
            out_energy_m = dash.no_update

            if trigger == "geo-energy-select-desktop":
                active_energy = energy_d
                out_energy_m = energy_d

            elif trigger == "geo-energy-select-mobile":
                active_energy = energy_m
                out_energy_d = energy_m

            if (
                not year
                or not active_energy
                or not metric
            ):
                return (
                    dash.no_update,
                    out_energy_d,
                    out_energy_m,
                )

            figure = self._get_choropleth(
                year_range=year,
                energy=active_energy,
                metric=metric,
                theme=current_theme,
            )

            return (
                figure,
                out_energy_d,
                out_energy_m,
            )

        @callback(
            Output(
                "geo-play-interval",
                "disabled",
            ),
            Output(
                "geo-play-btn",
                "children",
            ),
            Input(
                "geo-play-btn",
                "n_clicks",
            ),
            State(
                "geo-play-interval",
                "disabled",
            ),
            prevent_initial_call=True,
        )
        def toggle_play(
            _,
            is_disabled,
        ):
            if is_disabled:
                return (
                    False,
                    DashIconify(
                        icon="tabler:player-pause",
                        width=18,
                    ),
                )

            return (
                True,
                DashIconify(
                    icon="tabler:player-play",
                    width=18,
                ),
            )

        @callback(
            Output(
                "geo-year-slider",
                "value",
                allow_duplicate=True,
            ),
            Input(
                "geo-play-interval",
                "n_intervals",
            ),
            State(
                "geo-year-slider",
                "value",
            ),
            prevent_initial_call=True,
        )
        def advance_slider(
            n_intervals,
            current_range,
        ):
            if not current_range:
                return dash.no_update

            start_year = int(
                current_range[0]
            )

            end_year = int(
                current_range[-1]
            )

            width = end_year - start_year

            if end_year < self.max_year:
                return [
                    start_year + 1,
                    end_year + 1,
                ]

            new_start = self.min_year

            new_end = min(
                self.min_year + width,
                self.max_year,
            )

            return [
                new_start,
                new_end,
            ]