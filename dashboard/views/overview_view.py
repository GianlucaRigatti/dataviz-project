import dash_mantine_components as dmc
from dash_iconify import DashIconify

class OverviewView:
    def render_content(self, series_config: list[dict]) -> dmc.Stack:
        series_names = [s["name"] for s in series_config]

        legend = dmc.Group([
            dmc.ChipGroup(
                [
                    dmc.Chip(
                        s["name"],
                        value=s["name"],
                        size="sm",
                        variant="light",
                        color=s["color"].split(".")[0],
                        icon=DashIconify(icon="tabler:circle-filled"),
                    )
                    for s in series_config
                ],
                id="overview-series-filter",
                multiple=True,
                value=series_names,
            )
        ], justify="right", mb="sm", gap="xs")

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
                dmc.Title("New Car Registrations Overview", order=2, fw=900),
                dmc.Text([
                    "This dashboard explores the adoption of electrified power trains in the European passenger car market over time. "
                    "The charts compare the total raw number of registrations extracted from the ",
                    dmc.Anchor(
                        "EEA's Monitoring of CO2 emissions from passenger cars Regulation (EU) 2019/631", 
                        href="https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b", 
                        target="_blank",
                        underline = "not-hover",
                    ),
                    " dataset with the ones obtained through a baseline normalisation and an autoencoder-based normalisation procedure which aim to provide "
                    "a more accurate metric that accounts for the market choice available to the consumer when purchasing a new car."
                ]),
                dmc.Text([
                    "This we believe has an effect on the adoption of a specific power train type, as the technical characteristics and number of available models "
                    "provides consumers with more opportunities to decide for a specific motor energy category. "
                    "Use the filters to explore individual countries or the EU as a whole, adjust the time period window and select the power trains to compare."
                ])
            ], gap="md", mb="sm"),

            dmc.Card(
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
                    legend,
                    dmc.LineChart(
                        id="overview-timeseries-raw-chart",
                        h=200,
                        dataKey="year",
                        data=[],
                        series=series_config,
                        withLegend=False,
                        curveType="monotone",
                        tickLine="y",
                        tooltipAnimationDuration=190,
                        lineProps={
                            "isAnimationActive": True,
                            "animationDuration": 200,
                            "animationEasing": "ease",
                            "animationBegin": 100,
                        },
                        strokeWidth=3,
                        dotProps={"r": 4},
                        activeDotProps={
                            "r": 6,
                            "strokeWidth": 1,
                            "fill": "var(--mantine-color-body)"
                        },
                        lineChartProps={
                            "syncId": "market-evolution-charts"
                        },
                    ),

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
                    dmc.LineChart(
                        id="overview-timeseries-baseline-chart",
                        h=200,
                        dataKey="year",
                        data=[],
                        series=series_config,
                        withLegend=False,
                        curveType="monotone",
                        tickLine="y",
                        tooltipAnimationDuration=190,
                        lineProps={
                            "isAnimationActive": True,
                            "animationDuration": 200,
                            "animationEasing": "ease",
                            "animationBegin": 100,
                        },
                        strokeWidth=3,
                        dotProps={"r": 4},
                        activeDotProps={
                            "r": 6,
                            "strokeWidth": 1,
                            "fill": "var(--mantine-color-body)"
                        },
                        lineChartProps={
                            "syncId": "market-evolution-charts"
                        },
                    ),

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
                    dmc.LineChart(
                        id="overview-timeseries-autoencoder-chart",
                        h=200,
                        dataKey="year",
                        data=[],
                        series=series_config,
                        withLegend=False,
                        curveType="monotone",
                        tickLine="y",
                        tooltipAnimationDuration=190,
                        lineProps={
                            "isAnimationActive": True,
                            "animationDuration": 200,
                            "animationEasing": "ease",
                            "animationBegin": 100,
                        },
                        strokeWidth=3,
                        dotProps={"r": 4},
                        activeDotProps={
                            "r": 6,
                            "strokeWidth": 1,
                            "fill": "var(--mantine-color-body)"
                        },
                        lineChartProps={
                            "syncId": "market-evolution-charts"
                        },
                    ),
                ], gap="md", m={"base": "sm", "md": "md"}),
                p={"base": "lg", "md": "xl"},
            ),

            dmc.Stack([
                    dmc.Title("How to Read the Charts", order=3, fw=800),
                    dmc.Text("The three charts provide complementary views of the market. "),

                    dmc.Text([dmc.Text("Passenger Car Registrations", span=True, fw=800), " shows the number of new vehicles registered. "]),

                    dmc.Text([dmc.Text("Baseline Normalisation", span=True, fw=800),
                    " adjusts registrations according to the number of different vehicle and powertrain combinations available. This helps distinguish changes in registrations from changes in the range of products being     offered. "]),

                    dmc.Text([dmc.Text("Autoencoder Normalisation", span=True, fw=800),
                    " takes this idea a step further. Vehicle characteristics such as model, engine size and power are used to create a map of the available cars. Similar cars are placed close together, while cars with  substantially different characteristics occupy different areas of the map. The map is divided into a grid, and the occupied areas provide an estimate of how much market choice is available for each    powertrain."]),
                dmc.Card(
                    dmc.Stack([
                        dmc.Text([
                            "For example, across the European market, ",
                            dmc.Text("electric car registrations", span=True, fw=800),
                            " observed an increase in ",
                            dmc.Text("2023", span=True, fw=800),
                            " while baseline normalised registrations per unique option followed an opposing trend."
                            "This suggests that the growth of popularity of electric vehicles is accompanied by a growth in the number of available electric configurations, "
                            "meaning that the observed increase in adoption may not only reflect an increase in electrified vehicle demand but "
                            "also a structural change in car market offerings."
                        ]),
                        dmc.Text(
                            [
                                "The evolution in the number of unique options can be explored in the ",
                                dmc.Text("Volume", span=True, fw=800),
                                " page of the dashboard."
                            ],
                            fs="italic",
                            c="dimmed"
                        )
                    ], gap="md", m={"base": "sm", "md": "md"}), 
                    p={"base": "lg", "md": "xl"},
                    style={
                        "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                    },
                ),
            ], gap="md", mt="md", mb="md"),

            dmc.Stack([
                dmc.Title("New Car Registrations Market Composition and Market Demand Relative to Available Choice", order=2, fw=900),
                dmc.Text([
                    "The three charts compare the market composition across motor energy categories based on raw registrations "
                    "and normalised values. The normalised metrics provide an indication of ",
                    dmc.Text("demand", span=True, fw=800),
                    " as they take into account both registrations and a normalisation factor chosen to approximate market choice. For instance, a power train that "
                    "maintains a high normalised share after accounting for the number of available options may indicate stronger demand relative to its market offering "
                    "(i.e. it is both capturing new markets with a broader offering and strengthening its existing base)."
                ], mb="sm"),
                dmc.Card(
                    dmc.Stack([
                        dmc.Text([
                            "For instance, a power train that maintains a high normalised share after accounting for the number of available options "
                            "may indicate stronger demand relative to its market offering ",
                            dmc.Text("(i.e. it is both capturing new markets with a broader offering and strengthening its existing base)", 
                                span=True,
                                fs="italic"
                            ),
                            "."
                        ]),
                        dmc.Text([
                            "Comparing the share of the same motor energy category across the three pies can reveal whether a power train's market share can be "
                            "attributed to a broad range of available vehicle options or can be understood as a true consumer preference."
                        ])
                    ], gap="md", m={"base": "sm", "md": "md"}), 
                    p={"base": "lg", "md": "xl"},
                    style={
                        "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                    },
                    mb="sm",
                ),
                dmc.Text([
                    "Select a year within the time period and a region to compare the composition of the passenger car market across motor energy categories."
                ])
            ], gap="md", mb="sm"),

            dmc.Card(
                dmc.Stack([
                    dmc.Group(
                        [
                            dmc.Stack(
                                [
                                    dmc.Select(
                                        id="overview-pie-year-select",
                                        data=[],
                                        value=None,
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
                                    dmc.PieChart(
                                        id="overview-pie-raw-chart",
                                        data=[],
                                        withLabelsLine=True,
                                        labelsPosition="outside",
                                        labelsType="percent",
                                        withLabels=True,
                                        pieProps={"isAnimationActive": True},
                                    )
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
                                    dmc.PieChart(
                                        id="overview-pie-baseline-chart",
                                        data=[],
                                        withLabelsLine=True,
                                        labelsPosition="outside",
                                        labelsType="percent",
                                        withLabels=True,
                                        pieProps={"isAnimationActive": True},
                                    )
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
                                    dmc.PieChart(
                                        id="overview-pie-autoencoder-chart",
                                        data=[],
                                        withLabelsLine=True,
                                        labelsPosition="outside",
                                        labelsType="percent",
                                        withLabels=True,
                                        pieProps={"isAnimationActive": True},
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

    def render_filters(self, min_year: int, max_year: int, geo_options: list[dict], default_geo: str, suffix: str = "desktop") -> dmc.Stack:
        year_diff = max_year - min_year
        label_interval = 5 if year_diff >= 15 else (3 if year_diff >= 6 else 1)

        marks = []
        for y in range(min_year, max_year + 1):
            is_labeled = (y == min_year) or (y == max_year) or ((y - min_year) % label_interval == 0)
            marks.append({"value": y, "label": str(y)} if is_labeled else {"value": y})

        return dmc.Stack([
            dmc.Card(
                dmc.Stack([
                    dmc.Text("TIME PERIOD", ml="xs", size="sm", fw=700),
                    dmc.RangeSlider(
                        id=f"overview-year-slider-{suffix}",
                        min=min_year,
                        max=max_year,
                        value=[min_year, max_year],
                        step=1,
                        minRange=1,
                        marks=marks,
                        ml="xs",
                        mr="xs",
                        size="md",
                    )
                ]),
                p="md",
                pb="xl"
            ),
            dmc.Card(
                dmc.Stack([
                    dmc.Text("REGION", ml="xs", size="sm", fw=700),
                    dmc.Select(
                        id=f"overview-geo-select-{suffix}",
                        data=geo_options,
                        value=default_geo,
                        searchable=True,
                        clearSearchOnFocus=True,
                        nothingFoundMessage="Nothing found...",
                        clearable=False,
                        allowDeselect=False,
                        comboboxProps={"transitionProps": {"transition": "pop", "duration": 200}, "shadow": "sm"},
                        leftSectionPointerEvents="none",
                        leftSection=DashIconify(icon="tabler:world-pin"),
                        variant="filled",
                    )
                ]),
                p="md"
            )
        ], gap="md")