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
            dmc.Card(
                dmc.Stack([
                    dmc.Text("Overview", size="xl"),
                    dmc.Text("Add description here..."),
                ], gap="sm"),
                withBorder=True,
                shadow="sm",
                p="lg",
                pl="xl",
                pr="xl",
            ),
            dmc.Card(
                dmc.Stack([
                    dmc.Text("RAW REGISTRATION COUNTS"),
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
                        activeDotProps={"r": 6, "strokeWidth": 1, "fill": "var(--mantine-color-body)"},
                        lineChartProps={"syncId": "market-evolution-charts"},
                    ),
                    dmc.Text("BASELINE NORMALISATION COUNTS"),
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
                        activeDotProps={"r": 6, "strokeWidth": 1, "fill": "var(--mantine-color-body)"},
                        lineChartProps={"syncId": "market-evolution-charts"},
                    ),
                    dmc.Text("AUTOENCODER NORMALISATION COUNTS"),
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
                        activeDotProps={"r": 6, "strokeWidth": 1, "fill": "var(--mantine-color-body)"},
                        lineChartProps={"syncId": "market-evolution-charts"},
                    ),
                ], gap="sm", pb="xl"),
                withBorder=True,
                shadow="sm",
                p="lg",
                pl="xl",
                pr="xl",
            )
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
                    dmc.Text("TIME PERIOD", ml="xs"),
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
                withBorder=True,
                shadow="sm",
                p="md",
                pb="xl"
            ),
            dmc.Card(
                dmc.Stack([
                    dmc.Text("REGION", ml="xs"),
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
                withBorder=True,
                shadow="sm",
                p="md"
            )
        ], gap="md")