import dash_mantine_components as dmc

class OverviewView:
    def render_content(self) -> dmc.Stack:
        return dmc.Stack([
            dmc.Text("Market Evolution: ICE vs. Electrified Vehicles", size="xl"),
            dmc.Card(
                id="overview-timeseries-chart-card",
                withBorder=True,
                shadow="sm"
            )
        ], gap="sm")

    def render_filters(self) -> dmc.Stack:
        return dmc.Stack([
            dmc.Card(
                id="overview-year-filter-card",
                withBorder=True,
                shadow="sm"
            ),
            dmc.Card(
                id="overview-geo-filter-card",
                withBorder=True,
                shadow="sm"
            )
        ], gap="sm")