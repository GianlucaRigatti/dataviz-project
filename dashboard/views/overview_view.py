import dash_mantine_components as dmc
from dash_iconify import DashIconify

class OverviewView:
    def render_content(self, initial_data: list[dict], series_config: list[dict]) -> dmc.Stack:
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

        return dmc.Stack([
            dmc.Stack([
                dmc.Title("New Car Registrations Overview", order=2, fw=900),
                dmc.Text([
                    "Explore the adoption of electrified power trains in the European passenger car market over time. "
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
                    dmc.Title("Passenger Car Registrations", order=4, fw=800),
                    legend,
                    dmc.LineChart(
                        id="overview-timeseries-raw-chart",
                        h=200,
                        dataKey="year",
                        data=initial_data,
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
                        data=initial_data,
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
                                "Total Registrations / Market Variety Volume",
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
                        data=initial_data,
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
                dmc.Text([
                    "The three charts provide complementary views of the market. ",
                    dmc.Text("Passenger Car Registrations", span=True, fw=800),
                    " shows the number of new vehicles registered, while the ",
                    dmc.Text("Baseline Normalisation", span=True, fw=800),
                    " and ",
                    dmc.Text("Autoencoder Normalisation", span=True, fw=800),
                    " account for the variety of vehicle options (engine power, engine size and model) available and utility offered for each motor energy "
                    "category respectively. Comparing these trends helps distinguish whether a power train is gaining registrations because consumers are choosing it "
                    "more frequently, or because the range of available alternatives is changing."
                ], mb="sm"),

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
                    mb="sm",
                ),

                dmc.Title("New Car Registrations Market Composition and Market Demand Relative to Available Choice", order=2, fw=900),
                
            ], gap="md", mt="md")
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