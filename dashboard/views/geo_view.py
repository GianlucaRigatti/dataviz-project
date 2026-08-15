import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

class GeoView:
    def render_content(self, min_year: int, max_year: int) -> dmc.Stack:
        year_diff = max_year - min_year
        label_interval = 5 if year_diff >= 15 else (3 if year_diff >= 6 else 1)

        marks = []
        for y in range(min_year, max_year + 1):
            is_labeled = (y == min_year) or (y == max_year) or ((y - min_year) % label_interval == 0)
            marks.append({"value": y, "label": str(y)} if is_labeled else {"value": y})

        return dmc.Stack([
            dmc.Stack([
                dmc.Title("Geographical Distribution", order=2, fw=900),
                dmc.Text("Add description here..."),
            ], gap="md", mb="xs"),

            dmc.Card(
                dmc.Stack([
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                dmc.Card(
                                    dmc.Group([
                                        dmc.ActionIcon(
                                            DashIconify(icon="tabler:player-play", width=24),
                                            id="geo-play-btn",
                                            size="xl",
                                            variant="gradient",
                                            color="blue.6",
                                            radius="md",
                                            n_clicks=0
                                        ),
                                        dmc.RangeSlider(
                                            id="geo-year-slider",
                                            min=min_year,
                                            max=max_year,
                                            value=[min_year, max_year],
                                            step=1,
                                            minRange=1,
                                            marks=marks,
                                            size="md",
                                            style={"flex": 1},
                                        ),
                                        dcc.Interval(
                                            id="geo-play-interval", 
                                            interval=2000,
                                            disabled=True
                                        )
                                    ], align="center", gap="lg"),
                                    p="md",
                                    style={
                                        "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                                    },
                                ),
                                span={"base": 12, "md": 8}
                            ),
                            dmc.GridCol(
                                dmc.Flex(
                                    dmc.Paper( 
                                        dmc.SegmentedControl(
                                            id="geo-metric-select",
                                            data=[
                                                {
                                                    "label": dmc.Stack([
                                                        DashIconify(icon="tabler:database", width=20),
                                                        dmc.Text("Raw", size="sm")
                                                    ], align="center", p="xs", gap="0.1875rem"), 
                                                    "value": "raw"
                                                },
                                                {
                                                    "label": dmc.Stack([
                                                        DashIconify(icon="tabler:chart-line", width=20),
                                                        dmc.Text("Baseline", size="sm")
                                                    ], align="center", p="xs", gap="0.1875rem"), 
                                                    "value": "baseline"
                                                },
                                                {
                                                    "label": dmc.Stack([
                                                        DashIconify(icon="tabler:polygon", width=20),
                                                        dmc.Text("Autoencoder", size="sm")
                                                    ], align="center", p="xs", gap="0.1875rem"), 
                                                    "value": "autoencoder"
                                                }
                                            ],
                                            value="raw",
                                            fullWidth=True,
                                            size="sm",
                                            radius="md",
                                            color="blue.6",
                                            withItemsBorders=False,
                                            style={
                                                "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                                            },
                                        ),
                                        shadow="lg",
                                        radius="md",
                                    ),
                                    justify={"base": "center", "md": "flex-end"},
                                    w="100%",
                                    h="100%"
                                ),
                                span={"base": 12, "md": 4}
                            ),
                        ], 
                        align="center", 
                        mb="sm",
                        gutter="lg"
                    ),
                    dcc.Graph(
                        id="geo-map-chart",
                        responsive=True,
                        style={"height": "100%", "width": "100%"}
                    ),
                ], gap="md", m={"base": "sm", "md": "md"}, style={"height": "100%"}),
                p={"base": "lg", "md": "xl"},
                h={"base": 450, "md": 650},
            )
        ], gap="sm")

    def render_filters(self, energy_options: list[dict], default_energy: str | list, suffix: str = "desktop") -> dmc.Stack:
        default_values = [default_energy] if isinstance(default_energy, str) else default_energy

        return dmc.Stack([
            dmc.Card(
                dmc.Stack([
                    dmc.Text("MOTOR ENERGY", ml="xs", size="sm", fw=700),
                    dmc.MultiSelect(
                        id=f"geo-energy-select-{suffix}",
                        data=energy_options,
                        value=default_values,
                        searchable=False,
                        clearable=False,
                        hidePickedOptions=True,
                        clearSearchOnChange=False,
                        comboboxProps={"transitionProps": {"transition": "pop", "duration": 200}, "shadow": "sm"},
                        leftSectionPointerEvents="none",
                        leftSection=DashIconify(icon="tabler:car-turbine"),
                        variant="filled",
                    )
                ]),
                p="md"
            )
        ], gap="md")