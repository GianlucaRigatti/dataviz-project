import dash
from dash import callback, ctx, Input, Output, State
import dash_mantine_components as dmc
import pydeck as pdk
import pandas as pd
import pycountry
from dash_iconify import DashIconify

from views.geo_view import GeoView
from utils.data_loader import get_dataframe

EU_COORDS = {
    "AUT": [16.37, 48.20], "BEL": [4.35, 50.85], "BGR": [23.32, 42.69],
    "HRV": [15.98, 45.81], "CYP": [33.38, 35.18], "CZE": [14.43, 50.07],
    "DNK": [12.56, 55.67], "EST": [24.75, 59.43], "FIN": [24.93, 60.16],
    "FRA": [2.35, 48.85], "DEU": [13.40, 52.52], "GRC": [23.72, 37.98],
    "HUN": [19.04, 47.49], "IRL": [-6.26, 53.34], "ITA": [12.49, 41.90],
    "LVA": [24.10, 56.94], "LTU": [25.27, 54.68], "LUX": [6.13, 49.61],
    "MLT": [14.51, 35.89], "NLD": [4.90, 52.36], "POL": [21.01, 52.23],
    "PRT": [-9.13, 38.72], "ROU": [26.10, 44.42], "SVK": [17.10, 48.14],
    "SVN": [14.50, 46.05], "ESP": [-3.70, 40.41], "SWE": [18.06, 59.32],
    "GBR": [-0.12, 51.50], "NOR": [10.75, 59.91], "CHE": [7.44, 46.94]
}

class GeoController:
    def __init__(self):
        self.view = GeoView()
        self._load_data()
        self._register_callbacks()

    def _load_data(self):
        self.df = get_dataframe()
        self.geo_df = self.df[~self.df["geo"].isin(["EU27_2020", "EU28", "EU"])].copy()
        
        def get_iso3(iso2):
            mapping = {"UK": "GB", "EL": "GR"}
            iso2 = mapping.get(iso2, iso2)
            country = pycountry.countries.get(alpha_2=iso2)
            return country.alpha_3 if country else None
            
        self.geo_df["iso3"] = self.geo_df["geo"].apply(get_iso3)
        self.geo_df["lon"] = self.geo_df["iso3"].apply(lambda x: EU_COORDS.get(x, [None, None])[0])
        self.geo_df["lat"] = self.geo_df["iso3"].apply(lambda x: EU_COORDS.get(x, [None, None])[1])
        self.geo_df = self.geo_df.dropna(subset=["lon", "lat"])

        self.min_year = int(self.geo_df["TIME_PERIOD"].min())
        self.max_year = int(self.geo_df["TIME_PERIOD"].max())
        
        energies = self.geo_df["Motor energy"].dropna().unique()
        self.energy_options = [{"value": e, "label": e} for e in energies]
        self.energy_options.sort(key=lambda x: x["label"])
        
        self.default_energy = self.energy_options[0]["value"] if self.energy_options else None
        self.default_year = self.max_year

    def _get_deck_payload(self, year: int, energy: str, theme: str = "light"):
        if not year or not energy:
            return dash.no_update

        filtered = self.geo_df[
            (self.geo_df["TIME_PERIOD"] == year) & 
            (self.geo_df["Motor energy"] == energy)
        ]

        country_data = filtered.groupby(["Geopolitical entity (reporting)", "lon", "lat"], as_index=False)["registrations"].sum()
        max_val = self.geo_df["registrations"].max() or 1
        elevation_scale = 1000000 / max_val if max_val > 0 else 1

        layer = pdk.Layer(
            "ColumnLayer",
            data=country_data,
            get_position=["lon", "lat"],
            get_elevation="registrations",
            elevation_scale=elevation_scale,
            radius=40000,
            get_fill_color=[34, 139, 230, 200] if theme == "light" else [77, 171, 247, 220],
            pickable=True,
            auto_highlight=True,
            extruded=True,
        )
        
        view_state = pdk.ViewState(
            latitude=50.0,
            longitude=10.0,
            zoom=3.0,
            pitch=45,
            bearing=0
        )

        carto_style = (
            "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
            if theme == "light"
            else "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_provider="carto",
            map_style=carto_style,
            tooltip={"html": "<b>{Geopolitical entity (reporting)}</b><br/>Registrations: {registrations}"}
        )

        # Return raw Deck.gl JSON object/string directly
        return deck.to_json()

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack, dmc.Stack]:
        initial_map_json = self._get_deck_payload(self.default_year, self.default_energy, theme="light")
        
        content = self.view.render_content(initial_map_json)
        filters_desktop = self.view.render_filters(
            self.min_year, self.max_year, self.energy_options, self.default_year, self.default_energy, suffix="desktop"
        )
        filters_mobile = self.view.render_filters(
            self.min_year, self.max_year, self.energy_options, self.default_year, self.default_energy, suffix="mobile"
        )

        return content, filters_desktop, filters_mobile

    def _register_callbacks(self):
        @callback(
            Output("geo-map-chart", "data"), # <--- Directly target map data!
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

            updated_deck_json = self._get_deck_payload(active_year, active_energy, theme=current_theme)

            return (
                updated_deck_json,
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