import dash
from dash import callback, ctx, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.express as px
import numpy as np

from views.geo_view import GeoView
from utils.data_loader import ( 
    get_dataframe,
    extract_baseline_factors, 
    compute_baseline_normalization, 
    generate_latent_dataframe_pandas, 
    compute_grid_normalisation
)

class GeoController:
    def __init__(self):
        dmc.add_figure_templates()
        self.view = GeoView()
        self._load_data()
        self._register_callbacks()

    def _load_data(self):
        self.df = get_dataframe()
        self.min_year = int(self.df["TIME_PERIOD"].min())
        self.max_year = int(self.df["TIME_PERIOD"].max())

        self.geo_df = self.df[~self.df["geo"].isin(["EU27_2020", "EU28", "EU"])].copy()

        import pycountry
        def get_iso3(iso2):
            mapping = {"UK": "GB", "EL": "GR"}
            iso2 = mapping.get(iso2, iso2)
            country = pycountry.countries.get(alpha_2=iso2)
            return country.alpha_3 if country else None

        self.geo_df["iso3"] = self.geo_df["geo"].apply(get_iso3)
        self.geo_df = self.geo_df.dropna(subset=["iso3"])

        # Pre-compute Baseline Normalisation
        try:
            baseline_factors = extract_baseline_factors(self.geo_df)
            baseline_summary = compute_baseline_normalization(self.geo_df, factors_df=baseline_factors)
            self.geo_df = self.geo_df.merge(
                baseline_summary[["geo", "TIME_PERIOD", "Motor energy", "baseline_normalized_registrations"]],
                on=["geo", "TIME_PERIOD", "Motor energy"],
                how="left"
            )
        except Exception as e:
            print(f"Warning: Baseline calculation skipped - {e}")
            self.geo_df["baseline_normalized_registrations"] = self.geo_df["registrations"]

        # Pre-compute Autoencoder Normalisation
        try:
            enriched_pdf = generate_latent_dataframe_pandas(self.geo_df)
            norm_summary = compute_grid_normalisation(enriched_pdf, grid_size=0.2, min_registrations=10)
            self.geo_df = self.geo_df.merge(
                norm_summary[["geo", "TIME_PERIOD", "Motor energy", "normalized_registrations"]],
                on=["geo", "TIME_PERIOD", "Motor energy"],
                how="left"
            )
        except Exception as e:
            print(f"Warning: Autoencoder calculation skipped - {e}")
            self.geo_df["normalized_registrations"] = self.geo_df["registrations"]

        energies = self.geo_df["Motor energy"].dropna().unique()
        self.energy_options = [{"value": e, "label": e} for e in energies]
        self.energy_options.sort(key=lambda x: x["label"])
        self.default_energy = self.energy_options[0]["value"] if self.energy_options else None

    def _get_choropleth(self, year: int, energy: str, metric: str = "raw", theme: str = "light"):
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
            )[["registrations", "baseline_normalized_registrations", "normalized_registrations"]]
            .sum()
        )

        if metric == "baseline":
            val_col = "baseline_normalized_registrations"
            hover_label = "Baseline Normalized"
        elif metric == "autoencoder":
            val_col = "normalized_registrations"
            hover_label = "Autoencoder Normalized"
        else:
            val_col = "registrations"
            hover_label = "Registrations"

        country_data[val_col] = country_data[val_col].fillna(0)
        country_data["log_val"] = np.log10(country_data[val_col].clip(lower=1))

        fig = px.choropleth(
            country_data,
            locations="iso3",
            locationmode="ISO-3",
            color="log_val",
            hover_name="Geopolitical entity (reporting)",
            color_continuous_scale="Blues",
            labels={"log_val": hover_label},
            projection="natural earth",
        )

        num_format = ",.2f" if metric != "raw" else ",.0f"
        fig.update_traces(
            hovertemplate=(f"<b>%{{hovertext}}</b>, %{{customdata:{num_format}}}"),
            customdata=country_data[val_col],
        )

        fig.update_geos(
            fitbounds="locations",
            showland=True,
            showframe=False,
            showocean=True,
            showcountries=True,
            showcoastlines=True
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            template="mantine_dark" if theme == "dark" else "mantine_light",
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig

    def get_layouts(self):
        content = self.view.render_content(
            self.min_year,
            self.max_year
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

        return content, filters_desktop, filters_mobile

    def _register_callbacks(self):
        @callback(
            Output("geo-map-chart", "figure"),
            Output("geo-energy-select-desktop", "value"),
            Output("geo-energy-select-mobile", "value"),
            Input("geo-year-slider", "value"),
            Input("geo-metric-select", "value"),
            Input("geo-energy-select-desktop", "value"),
            Input("geo-energy-select-mobile", "value"),
            Input("color-scheme-switch", "computedColorScheme"),
            prevent_initial_call=True
        )
        def update_map(year, metric, energy_d, energy_m, theme_state):
            trigger = ctx.triggered_id
            current_theme = "dark" if theme_state == "dark" else "light"

            active_energy = energy_d if energy_d else energy_m
            out_energy_d, out_energy_m = dash.no_update, dash.no_update

            if trigger == "geo-energy-select-desktop":
                active_energy, out_energy_m = energy_d, energy_d
            elif trigger == "geo-energy-select-mobile":
                active_energy, out_energy_d = energy_m, energy_m

            if not year or not active_energy or not metric:
                return dash.no_update, out_energy_d, out_energy_m

            updated_figure = self._get_choropleth(
                year,
                active_energy,
                metric,
                theme=current_theme
            )

            return updated_figure, out_energy_d, out_energy_m

        @callback(
            Output("geo-play-interval", "disabled"),
            Output("geo-play-btn", "children"),
            Input("geo-play-btn", "n_clicks"),
            State("geo-play-interval", "disabled"),
            prevent_initial_call=True
        )
        def toggle_play(_, is_disabled):
            if is_disabled:
                return False, DashIconify(icon="tabler:player-pause", width=18)
            else:
                return True, DashIconify(icon="tabler:player-play", width=18)

        @callback(
            Output("geo-year-slider", "value", allow_duplicate=True),
            Input("geo-play-interval", "n_intervals"),
            State("geo-year-slider", "value"),
            prevent_initial_call=True
        )
        def advance_slider(n_intervals, current_year):
            if current_year >= self.max_year:
                return self.min_year
            return current_year + 1