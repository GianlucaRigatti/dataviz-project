import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc

class VolumeView:

    def render_content(self, initial_factors_data: list[dict], initial_latent_data: list[dict], initial_manufacturer_table_data: list[dict], initial_latent_scatter_figure, series_config: list[dict]) -> dmc.Stack:
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
                    id="volume-series-filter",
                    multiple=True,
                    value=series_names,
                )
            ], justify="right", mb="sm", gap="xs")

        return dmc.Stack(
            [
                dmc.Stack([
                    dmc.Title("Normalisation Factors", order=2, fw=900),
                    dmc.Text([
                        "The normalisation factors provide a measure of the variety of vehicles available within each motor energy category. "
                    ]),
                    dmc.Text([
                        "The ",
                        dmc.Text("Baseline Normalisation Factor", span=True, fw=800),
                        " measures the number of unique vehicle configurations available within each motor energy category for a given year."
                        "A configuration is considered different when its model name, engine capacity, or engine power differs, meaning that the measure captures "
                        "differences in the main technical characteristics and model design of the vehicles available, while excluding minor equipment variations. "
                        "This gives an indication of how much variety is available to consumers, independently of how many vehicles were actually registered.",
                    ]),
                    dmc.Text([
                        "The ",
                        dmc.Text("Autoencoder Normalisation Factor", span=True, fw=800),
                        " measures instead the diversity of vehicles based solely on their technical characteristics. "
                        "Rather than counting distinct configurations, it measures how registrations are distributed across the active regions of the autoencoder's "
                        "latent space, providing an indication of the diversity of vehicle characteristics. "
                        "In simple terms, given an autoencoder learns to compress information, it shows how hard it was for the model to compress physical characteristics "
                        "relative to a specific motor energy type, the harder it was for the model, the more spread out the points, the more market choice is actually "
                        "available to the consumer from a utilitarian perspective. "
                    ]),
                ], gap="md", mb="sm"),
                dmc.Card(
                    dmc.Stack([
                        dmc.Title(
                            [
                                "Baseline Normalisation Factor",
                                dmc.Text(
                                    "Count of Unique Vehicle Configurations (Model + Engine Capacity + Engine Power)",
                                    fs="italic",
                                ),
                            ],
                            order=4,
                            fw=800
                        ),
                        legend,
                        dmc.LineChart(
                            id="volume-timeseries-factors-chart",
                            h=200,
                            dataKey="year",
                            data=initial_factors_data,
                            series=series_config,
                            withLegend=False,
                            curveType="monotone",
                            tickLine="y",
                            tooltipAnimationDuration=200,
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
                                "fill": "var(--mantine-color-body)",
                            },
                        ),

                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dmc.Title("Autoencoder Normalisation Factor", order=4, fw=800),
                                        dmc.Popover(
                                            [
                                                dmc.PopoverTarget(
                                                    DashIconify(
                                                        icon="tabler:info-square-rounded", 
                                                        width=20,
                                                        style={"cursor": "pointer", "color": "var(--mantine-color-dimmed)"}
                                                    )
                                                ),
                                                dmc.PopoverDropdown(
                                                    dmc.Text(
                                                        "The 'Alternative/Other' category may be omitted due to insufficient registration data.",
                                                        size="sm"
                                                    ),
                                                    style={
                                                        "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                                                    }
                                                ),
                                            ],
                                            width=250,
                                            position="bottom",
                                            withArrow=True,
                                            shadow="lg",
                                        )
                                    ],
                                    gap="xs"
                                ),
                                dmc.Text(
                                    "Registrations per Active Latent-Space Cell",
                                    fs="italic",
                                ),
                            ],
                            gap=0,
                        ),
                        dmc.LineChart(
                            id="volume-timeseries-latent-volume-chart",
                            h=200,
                            dataKey="year",
                            data=initial_latent_data,
                            series=series_config,
                            withLegend=False,
                            curveType="monotone",
                            tickLine="y",
                            tooltipAnimationDuration=200,
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
                                "fill": "var(--mantine-color-body)",
                            },
                        ),
                    ], gap="md", m={"base": "sm", "md": "md"}),
                    p={"base": "lg", "md": "xl"},
                ),

                dmc.Stack([
                    dmc.Title("Top 3 Manufacturers by Year", order=2, fw=900),
                    dmc.Text("The leading manufacturers by new passenger car registrations for each year."),
                ], gap="md", mt="md", mb="sm"),
                dmc.Card(
                    dmc.Stack([
                        dmc.Grid([
                            dmc.GridCol(
                                dmc.Table(
                                    [
                                        dmc.TableThead(
                                            dmc.TableTr([
                                                dmc.TableTh("Year"),
                                                dmc.TableTh("Top 3 Manufacturers (Registrations)"),
                                            ])
                                        ),
                                        dmc.TableTbody(
                                            id="volume-manufacturer-table",
                                            children=self.render_manufacturer_table(initial_manufacturer_table_data),
                                        ),
                                    ],
                                    striped=True,
                                    highlightOnHover=True,
                                    withTableBorder=True,
                                    horizontalSpacing="sm",
                                    verticalSpacing="xs",
                                ),
                                span={"base": 12, "md": 7},
                            ),
                            
                            dmc.GridCol(
                                dmc.Stack([
                                    dmc.Title("What the Manufacturer Rankings Reveal", order=3, fw=800),
                                    dmc.Text(
                                        "Comparing the ranking across years makes it possible to identify changes or stability in the passenger car market structure.", 
                                        mb="sm"
                                    ),
                                    dmc.Card(
                                        dmc.Stack([
                                            dmc.Text([
                                                "In particular, the appearance of new manufacturers in the top three may indicate the emergence of new players, that "
                                                "have been able to better capture and respond to the shifts in consumer needs."
                                            ]),
                                        ], gap="md", m={"base": "sm", "md": "md"}), 
                                        p={"base": "lg", "md": "xl"},
                                        style={
                                            "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                                        },
                                        mb="sm"
                                    ),
                                    dmc.Text(
                                        [
                                            dmc.Text("Note", span=True, fw=800),
                                            ": Manufacturer names may change over time due to mergers, "
                                            "acquisitions, or rebranding. As a result, comparability of manufacturers across years may be affected."
                                        ],
                                        fs="italic",
                                        c="dimmed",
                                    ),
                                ], gap="md"),
                                span={"base": 12, "md": 5},
                            ),
                        ], gutter="xl"),
                    ], gap="md", m={"base": "sm", "md": "md"}),
                    p={"base": "lg", "md": "xl"},
                ),

                dmc.Stack([
                    dmc.Title("Vehicle Characteristics in the Latent Space", order=2, fw=900),
                    dmc.Text(
                        "Each point represents a vehicle configuration, coloured by motor energy category, only the last year of the selected time period filtered is shown for performance reasons.",
                        fs="italic",
                        c="dimmed",
                        size="sm"
                    ),
                ], gap="md", mt="md", mb="sm"),
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text(
                                "The points are positioned according to the two-dimensional "
                                "representation learned by the autoencoder. Vehicles with "
                                "similar characteristics tend to appear closer together, "
                                "making broad patterns in the different motor energy categories "
                                "visible without performing any explicit clustering."
                            ),

                            dcc.Graph(
                                id="volume-latent-scatter-chart",
                                figure=initial_latent_scatter_figure,
                                config={
                                    "displayModeBar": False,
                                },
                                style={
                                    "width": "100%",
                                    "height": "500px",
                                },
                            ),
                        ],
                        gap="md",
                        m={"base": "sm", "md": "md"},
                    ),
                    p={"base": "lg", "md": "xl"},
                ),
            ],
            gap="sm",
        )

    def render_manufacturer_table(self, table_data: list[dict]):
        return [
            dmc.TableTr([
                dmc.TableTd(
                    row["year"],
                    style={
                        "fontWeight": 600,
                        "whiteSpace": "nowrap",
                    },
                ),
                dmc.TableTd(
                    dmc.Text([
                            child
                            for i, (manufacturer, registrations)
                            in enumerate(row["top_manufacturers"])
                            for child in [
                                dmc.Text(
                                    manufacturer,
                                    span=True,
                                    fw=600,
                                ),
                                f" ({registrations:,})",
                                ", " if i < len(row["top_manufacturers"]) - 1 else "",
                            ]
                    ], size="xs"),
                ),
            ])
            for row in table_data
        ]

    def render_filters(
        self,
        min_year: int,
        max_year: int,
        geo_options: list[dict],
        default_geo: str,
        suffix: str = "desktop",
    ) -> dmc.Stack:

        year_diff = max_year - min_year

        label_interval = (
            5
            if year_diff >= 15
            else (
                3
                if year_diff >= 6
                else 1
            )
        )

        marks = []

        for y in range(
            min_year,
            max_year + 1
        ):

            is_labeled = (
                (y == min_year)
                or (y == max_year)
                or (
                    (y - min_year)
                    % label_interval == 0
                )
            )

            marks.append(
                {
                    "value": y,
                    "label": str(y),
                }
                if is_labeled
                else {
                    "value": y
                }
            )

        return dmc.Stack(
            [
                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text(
                                "TIME PERIOD",
                                ml="xs",
                                size="sm", fw=700
                            ),

                            dmc.RangeSlider(
                                id=f"volume-year-slider-{suffix}",
                                min=min_year,
                                max=max_year,
                                value=[
                                    min_year,
                                    max_year
                                ],
                                step=1,
                                minRange=1,
                                marks=marks,
                                ml="xs",
                                mr="xs",
                                size="md",
                            ),
                        ]
                    ),
                    p="md",
                    pb="xl",
                ),

                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Text(
                                "REGION",
                                ml="xs",
                                size="sm", fw=700
                            ),

                            dmc.Select(
                                id=f"volume-geo-select-{suffix}",
                                data=geo_options,
                                value=default_geo,
                                searchable=True,
                                clearSearchOnFocus=True,
                                nothingFoundMessage="Nothing found...",
                                clearable=False,
                                allowDeselect=False,
                                comboboxProps={
                                    "transitionProps": {
                                        "transition": "pop",
                                        "duration": 200,
                                    },
                                    "shadow": "sm",
                                },
                                leftSectionPointerEvents="none",
                                leftSection=DashIconify(
                                    icon="tabler:world-pin"
                                ),
                                variant="filled",
                            ),
                        ]
                    ),
                    p="md",
                ),
            ],
            gap="md",
        )