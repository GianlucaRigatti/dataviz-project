import dash_mantine_components as dmc
import dash_deck
from dash import html, dcc
from dash_iconify import DashIconify

class GeoView:
    def render_content(self, initial_deck_json) -> dmc.Stack:
        return dmc.Stack([
            dmc.Stack([
                dmc.Title("Geographical Distribution", order=2, fw=900),
                dmc.Text("An interactive read of passenger car registrations across European nations.", c="dimmed"),
            ], gap="md", mb="sm"),
            
            dmc.Card(
                [
                    dash_deck.DeckGL(
                        initial_deck_json,
                        id="geo-map-chart",
                        tooltip=True,
                        style={"height": "100%", "width": "100%"},
                        mapboxKey=""
                    )
                ],
                style={"height": "600px", "width": "100%", "position": "relative", "overflow": "hidden"},
                p=0,
                withBorder=True,
                shadow="sm",
            )
        ], gap="sm")

    def render_filters(self, min_year: int, max_year: int, energy_options: list[dict], default_year: int, default_energy: str, suffix: str = "desktop") -> dmc.Stack:
        marks = [{"value": y, "label": str(y)} for y in range(min_year, max_year + 1) if y % 2 == 0 or y == min_year or y == max_year]

        return dmc.Stack([
            dmc.Card(
                dmc.Stack([
                    dmc.Text("TIME WHEEL", ml="xs", size="sm", fw=700, tt="uppercase", lts=1),
                    dmc.Group([
                        dmc.ActionIcon(
                            DashIconify(icon="tabler:player-play", width=20),
                            id=f"geo-play-btn-{suffix}",
                            size="lg",
                            variant="light",
                            color="blue",
                            n_clicks=0
                        ),
                        dmc.Slider(
                            id=f"geo-year-slider-{suffix}",
                            min=min_year,
                            max=max_year,
                            value=default_year,
                            step=1,
                            marks=marks,
                            size="md",
                            style={"flex": 1}
                        )
                    ], align="center", gap="md", mb=20),
                    dcc.Interval(
                        id=f"geo-play-interval-{suffix}", 
                        interval=1500, 
                        disabled=True
                    )
                ]),
                p="md",
            ),
            dmc.Card(
                dmc.Stack([
                    dmc.Text("MOTOR ENERGY", ml="xs", size="sm", fw=700, tt="uppercase", lts=1),
                    dmc.Select(
                        id=f"geo-energy-select-{suffix}",
                        data=energy_options,
                        value=default_energy,
                        searchable=True,
                        clearable=False,
                        allowDeselect=False,
                        leftSectionPointerEvents="none",
                        leftSection=DashIconify(icon="tabler:battery-automotive"),
                        variant="filled",
                    )
                ]),
                p="md"
            )
        ], gap="md")