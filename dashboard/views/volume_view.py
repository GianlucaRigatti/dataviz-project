import dash_mantine_components as dmc
from dash_iconify import DashIconify


class VolumeView:

    def render_content(
        self,
        initial_factors_data: list[dict],
        initial_yoy_data: list[dict],
        series_config: list[dict],
    ) -> dmc.Stack:

        series_names = [
            s["name"]
            for s in series_config
        ]

        legend = dmc.Group(
            [
                dmc.ChipGroup(
                    [
                        dmc.Chip(
                            s["name"],
                            value=s["name"],
                            size="sm",
                            variant="light",
                            color=s["color"].split(".")[0],
                            icon=DashIconify(
                                icon="tabler:circle-filled"
                            ),
                        )
                        for s in series_config
                    ],
                    id="volume-series-filter",
                    multiple=True,
                    value=series_names,
                )
            ],
            justify="right",
            mb="sm",
            gap="xs",
        )

        return dmc.Stack(
            [
                dmc.Stack(
                    [
                        dmc.Title(
                            "Normalisation Factors & Latent Volume",
                            order=2,
                            fw=1000,
                        ),
                        dmc.Text(
                            "Comparison of conventional market-choice "
                            "normalisation with year-over-year changes in "
                            "autoencoder latent-space occupancy."
                        ),
                    ],
                    gap="md",
                    mb="sm",
                ),

                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Title(
                                [
                                    "Baseline Normalisation Factor",
                                    dmc.Text(
                                        "Count of Unique Consumer Model Choices "
                                        "(Name + Capacity + Power)",
                                        fs="italic",
                                    ),
                                ],
                                order=3,
                            ),

                            legend,

                            dmc.LineChart(
                                id="volume-timeseries-factors-chart",
                                h=300,
                                dataKey="year",
                                data=initial_factors_data,
                                series=series_config,
                                withLegend=False,
                                curveType="monotone",
                                tickLine="y",
                                tooltipAnimationDuration=190,
                                strokeWidth=3,
                                dotProps={"r": 4},
                                activeDotProps={
                                    "r": 6,
                                    "strokeWidth": 1,
                                    "fill": "var(--mantine-color-body)",
                                },
                            ),
                        ],
                        gap="md",
                        m={"base": "sm", "md": "md"},
                    ),
                    p="xl",
                ),

                dmc.Card(
                    dmc.Stack(
                        [
                            dmc.Title(
                                [
                                    "Autoencoder Normalisation Factor",
                                    dmc.Text(
                                        "Total Registrations / Occupied Latent-Space Volume",
                                        fs="italic",
                                    ),
                                ],
                                order=3,
                            ),

                            dmc.LineChart(
                                id="volume-timeseries-yoy-chart",
                                h=300,
                                dataKey="year",
                                data=initial_yoy_data,
                                series=series_config,
                                withLegend=False,
                                curveType="monotone",
                                tickLine="y",
                                tooltipAnimationDuration=190,
                                strokeWidth=3,
                                dotProps={"r": 4},
                                activeDotProps={
                                    "r": 6,
                                    "strokeWidth": 1,
                                    "fill": "var(--mantine-color-body)",
                                },
                                referenceLines=[
                                    {
                                        "y": 0,
                                        "label": "No change",
                                        "color": "gray.5",
                                    }
                                ],
                            ),
                        ],
                        gap="md",
                        m={"base": "sm", "md": "md"},
                    ),
                    p="xl",
                ),
            ],
            gap="sm",
        )

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