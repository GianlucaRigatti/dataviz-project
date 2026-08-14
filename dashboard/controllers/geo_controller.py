import dash
from dash import callback, ctx, Input, Output, State
import dash_mantine_components as dmc
import pydeck as pdk
import pandas as pd
import pycountry
from dash_iconify import DashIconify
import plotly.express as px
from views.geo_view import GeoView
from utils.data_loader import get_dataframe
import numpy as np

class GeoController:
    def __init__(self):
        self.view = GeoView()
        self._load_data()
        self._register_callbacks()

    def _load_data(self):
        self.df = get_dataframe()

        self.geo_df = self.df[
            ~self.df["geo"].isin(["EU27_2020", "EU28", "EU"])
        ].copy()

        def get_iso3(iso2):
            mapping = {
                "UK": "GB",
                "EL": "GR",
            }

            iso2 = mapping.get(iso2, iso2)
            country = pycountry.countries.get(alpha_2=iso2)

            return country.alpha_3 if country else None

        self.geo_df["iso3"] = self.geo_df["geo"].apply(get_iso3)
        self.geo_df = self.geo_df.dropna(subset=["iso3"])

        self.min_year = int(self.geo_df["TIME_PERIOD"].min())
        self.max_year = int(self.geo_df["TIME_PERIOD"].max())

        energies = self.geo_df["Motor energy"].dropna().unique()

        self.energy_options = [
            {"value": e, "label": e}
            for e in energies
        ]
        self.energy_options.sort(key=lambda x: x["label"])

        self.default_energy = (
            self.energy_options[0]["value"]
            if self.energy_options
            else None
        )

        self.default_year = self.max_year

    def _get_choropleth(self, year: int, energy: str, theme: str = "light"):
        if not year or not energy:
            return {}

        filtered = self.geo_df[
            (self.geo_df["TIME_PERIOD"] == year) &
            (self.geo_df["Motor energy"] == energy)
        ]

        country_data = (
            filtered
            .groupby(
                ["iso3", "Geopolitical entity (reporting)"],
                as_index=False
            )["registrations"]
            .sum()
        )

        country_data["log_registrations"] = np.log10(
            country_data["registrations"].clip(lower=1)
        )

        fig = px.choropleth(
            country_data,
            locations="iso3",
            locationmode="ISO-3",
            color="log_registrations",
            hover_name="Geopolitical entity (reporting)",
            color_continuous_scale="Blues",
            labels={
                "log_registrations": "Registrations",
            },
            projection="natural earth",
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Registrations: %{customdata:,.0f}"
                "<extra></extra>"
            ),
            customdata=country_data["registrations"],
        )

        fig.update_geos(
            fitbounds="locations",
            showland=True,
            landcolor="#303030" if theme == "dark" else "#EDEDED",
            showocean=True,
            oceancolor="#181818" if theme == "dark" else "#FFFFFF",
            showcountries=True,
            countrycolor="#777777",
            showcoastlines=True,
            coastlinecolor="#777777",
        )

        tick_values = [
            1,
            10,
            100,
            1_000,
            10_000,
            100_000,
            1_000_000,
            10_000_000,
        ]

        max_registrations = country_data["registrations"].max()

        tick_values = [
            x for x in tick_values
            if x <= max_registrations
        ]

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            template="plotly_dark" if theme == "dark" else "plotly_white",
            coloraxis_colorbar=dict(
                title="Registrations",
                tickvals=np.log10(tick_values),
                ticktext=[f"{x:,.0f}" for x in tick_values],
                thickness=15,
            ),
        )

        return fig

    def get_layouts(self):
        content = self.view.render_content(None)

        filters_desktop = self.view.render_filters(
            self.min_year,
            self.max_year,
            self.energy_options,
            self.default_year,
            self.default_energy,
            suffix="desktop",
        )

        filters_mobile = self.view.render_filters(
            self.min_year,
            self.max_year,
            self.energy_options,
            self.default_year,
            self.default_energy,
            suffix="mobile",
        )

        return content, filters_desktop, filters_mobile

    def _register_callbacks(self):
        @callback(
            Output("geo-map-chart", "figure"),
            Output("geo-year-slider-desktop", "value"),
            Output("geo-year-slider-mobile", "value"),
            Output("geo-energy-select-desktop", "value"),
            Output("geo-energy-select-mobile", "value"),
            Input("geo-year-slider-desktop", "value"),
            Input("geo-year-slider-mobile", "value"),
            Input("geo-energy-select-desktop", "value"),
            Input("geo-energy-select-mobile", "value"),
            Input("color-scheme-switch", "computedColorScheme"),
            prevent_initial_call=True
        )
        def update_map(year_d, year_m, energy_d, energy_m, theme_state):
            trigger = ctx.triggered_id
            current_theme = "dark" if theme_state == "dark" else "light"

            if trigger == "geo-year-slider-desktop":
                active_year, active_energy = year_d, energy_d
                out_year_d, out_year_m = dash.no_update, year_d
                out_energy_d, out_energy_m = dash.no_update, dash.no_update
            elif trigger == "geo-year-slider-mobile":
                active_year, active_energy = year_m, energy_m
                out_year_d, out_year_m = year_m, dash.no_update
                out_energy_d, out_energy_m = dash.no_update, dash.no_update
            elif trigger == "geo-energy-select-desktop":
                active_year, active_energy = year_d, energy_d
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_energy_d, out_energy_m = dash.no_update, energy_d
            elif trigger == "geo-energy-select-mobile":
                active_year, active_energy = year_m, energy_m
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_energy_d, out_energy_m = energy_m, dash.no_update
            elif trigger == "color-scheme-switch":
                active_year = year_d if year_d else year_m
                active_energy = energy_d if energy_d else energy_m
                out_year_d, out_year_m = dash.no_update, dash.no_update
                out_energy_d, out_energy_m = dash.no_update, dash.no_update
            else:
                return [dash.no_update] * 5

            if not active_year or not active_energy:
                return [dash.no_update] * 5

            updated_figure = self._get_choropleth(
                active_year,
                active_energy,
                theme=current_theme
            )

            return (
                updated_figure,
                out_year_d,
                out_year_m,
                out_energy_d,
                out_energy_m
            )

        @callback(
            Output("geo-play-interval-desktop", "disabled"),
            Output("geo-play-btn-desktop", "children"),
            Input("geo-play-btn-desktop", "n_clicks"),
            State("geo-play-interval-desktop", "disabled"),
            prevent_initial_call=True
        )
        def toggle_play(n_clicks, is_disabled):
            if is_disabled:
                return False, DashIconify(icon="tabler:player-pause", width=20)
            else:
                return True, DashIconify(icon="tabler:player-play", width=20)

        @callback(
            Output("geo-year-slider-desktop", "value", allow_duplicate=True),
            Input("geo-play-interval-desktop", "n_intervals"),
            State("geo-year-slider-desktop", "value"),
            prevent_initial_call=True
        )
        def advance_slider(n_intervals, current_year):
            if current_year >= self.max_year:
                return self.min_year
            return current_year + 1