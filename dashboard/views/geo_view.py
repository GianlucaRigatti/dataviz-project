import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

class GeoView:

    def _render_purples_legend(self) -> dmc.Stack:
        purples = [
            "#fcfbfd",
            "#efedf5",
            "#dadaeb",
            "#bcbddc",
            "#9e9ac8",
            "#807dba",
            "#6a51a3",
            "#54278f",
            "#3f007d",
        ]

        gradient = ", ".join(
            f"{color} {i / (len(purples) - 1) * 100:.1f}%"
            for i, color in enumerate(purples)
        )

        return dmc.Stack(
            [
                dmc.Box(
                    style={
                        "height": "0.75rem",
                        "width": "100%",
                        "borderRadius": "999px",
                        "background": (
                            f"linear-gradient(90deg, {gradient})"
                        ),
                        "border": "1px solid var(--mantine-color-default-border)"
                    }
                ),

                dmc.Group(
                    [
                        dmc.Text(
                            "Lower",
                            size="xs",
                            c="dimmed",
                        ),
                        dmc.Text(
                            "Higher",
                            size="xs",
                            c="dimmed",
                        ),
                    ],
                    justify="space-between",
                ),
            ],
            gap="xs",
            w="90%",
        )

    def render_content(self, min_year: int, max_year: int, series_config: list) -> dmc.Stack:
        year_diff = max_year - min_year
        label_interval = 5 if year_diff >= 15 else (3 if year_diff >= 6 else 1)

        marks = []
        for y in range(min_year, max_year + 1):
            is_labeled = (y == min_year) or (y == max_year) or ((y - min_year) % label_interval == 0)
            marks.append({"value": y, "label": str(y)} if is_labeled else {"value": y})

        non_interactable_legend = dmc.Group(
            [
                dmc.Badge(
                    s["name"],
                    size="md",
                    variant="outline",
                    color=s["color"].split(".")[0],
                    leftSection=DashIconify(icon="tabler:circle-filled"),
                    style={"textTransform": "none", "cursor": "default"} 
                )
                for s in series_config
            ],
            justify="flex-end", mb="sm", gap="xs"
        )

        return dmc.Stack([
            dmc.Stack([
                dmc.Title("Geographical Distribution of New Car Registrations across the European Union", order=2, fw=900),
            ], gap="md", mb="sm"),

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
                                        dmc.Slider(
                                            id="geo-year-slider",
                                            min=min_year,
                                            max=max_year,
                                            value=max_year,
                                            step=1,
                                            marks=marks,
                                            size="md",
                                            style={"flex": 1},
                                            mb="md",
                                            mr="sm"
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
                                            radius="lg",
                                            color="blue.6",
                                            withItemsBorders=False,
                                            style={
                                                "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                                            },
                                        ),
                                        shadow="lg",
                                        radius="lg",
                                    ),
                                    justify={"base": "center", "md": "flex-end"},
                                    w="100%",
                                    h="100%",
                                ),
                                span={"base": 12, "md": 4}
                            ),
                        ], 
                        align="center", 
                        mb="sm",
                        gutter="lg"
                    ),
                    dmc.Stack(
                        [
                            dmc.Center(
                                self._render_purples_legend(),
                            ),
                            dcc.Graph(
                                id="geo-map-chart",
                                responsive=True,
                                style={
                                    "height": "100%",
                                    "width": "100%",
                                },
                            ),
                            
                        ],
                        gap="sm",
                        style={"flex": 1, "minHeight": 0},
                    ),
                ], gap="md", m={"base": "sm", "md": "md"}, style={"height": "100%"}),
                p={"base": "lg", "md": "xl"},
                h={"base": 550, "md": 700},
            ),

            dmc.Stack([
                dmc.Text([
                    "This page shows how new passenger car registrations are distributed across European countries for selected motor energies and year. "
                    "The map can display raw registrations or the two normalised measures introduced in the ",
                    dmc.Text("Overview", span=True, fw=800),
                    " page, allowing for a geographical understanding of the distribution of new cars across the European Union."
                ]),
            ], gap="md", mt="sm"),

            dmc.Stack([
                dmc.Title("Predominant Motor Energy across the European Union", order=2, fw=900),
                dmc.Text([
                    "These maps show the predominant motor energy category in each country based on total registrations and the two normalised measures. "
                    "Comparing the maps highlights whether the dominant power train changes when differences in motor energy availability are taken into account."
                ]),
            ], gap="md", mt="md", mb="sm"),

            dmc.Card(
                dmc.Stack([
                    dmc.Group(
                        [
                            dmc.Stack(
                                [
                                    dmc.Select(
                                        id="geo-predominant-maps-year-select",
                                        data=[
                                            {"label": str(y), "value": str(y)} 
                                            for y in range(min_year, max_year + 1)
                                        ],
                                        value=str(max_year),
                                        w=150,
                                        allowDeselect=False,
                                        searchable=False,
                                        clearable=False,
                                        comboboxProps={"transitionProps": {"transition": "pop", "duration": 200}, "shadow": "sm"},
                                        leftSectionPointerEvents="none",
                                        leftSection=DashIconify(icon="tabler:calendar-stats"),
                                        variant="filled",
                                    ),
                                    non_interactable_legend,
                                ],
                                gap="md", 
                                align="flex-end"
                            )
                        ],
                        justify="flex-end",
                    ),
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                dmc.Stack([
                                    dmc.Title(
                                        [
                                            "Passenger Car Registrations",
                                            dmc.Text(
                                                "Total Registrations",
                                                fs="italic"
                                            ),
                
                                        ],
                                        order=4,
                                        fw=800
                                    ),
                                    dcc.Graph(
                                        id="geo-predominant-maps-raw-chart",
                                        responsive=True,
                                        style={
                                            "height": "250px",
                                            "width": "100%",
                                        },
                                    ),
                                ], align="center", gap="xs"),
                                span={"base": 12, "md": 4}
                            ),
                            dmc.GridCol(
                                dmc.Stack([
                                    dmc.Title(
                                        [
                                            "Baseline Normalisation",
                                            dmc.Text(
                                                "Total Registrations / Unique Car Models and Power Train Configurations",
                                                fs="italic"
                                            ),
                                        ],
                                        order=4,
                                        fw=800
                                    ),
                                    dcc.Graph(
                                        id="geo-predominant-maps-baseline-chart",
                                        responsive=True,
                                        style={
                                            "height": "250px",
                                            "width": "100%",
                                        },
                                    ),
                                ], align="center", gap="xs"),
                                span={"base": 12, "md": 4}
                            ),
                            dmc.GridCol(
                                dmc.Stack([
                                    dmc.Title(
                                        [
                                            "Autoencoder Normalisation",
                                            dmc.Text(
                                                "Total Registrations / Available Market Choice",
                                                fs="italic"
                                            ),
                
                                        ],
                                        order=4,
                                        fw=800
                                    ),
                                    dcc.Graph(
                                        id="geo-predominant-maps-autoencoder-chart",
                                        responsive=True,
                                        style={
                                            "height": "250px",
                                            "width": "100%",
                                        }
                                    )
                                ], align="center", gap="xs"),
                                span={"base": 12, "md": 4}
                            ),
                        ],
                        gutter="xl",
                        align="center"
                    )
                ], gap="md", m={"base": "sm", "md": "md"}),
                p={"base": "lg", "md": "xl"},
            ),
            
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