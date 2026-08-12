import dash_mantine_components as dmc

class MarketVolumeView:
    def render_content(self):
        return dmc.Stack([
            dmc.Text("Market Volume Content Here.", size="lg")
        ])

    def render_filters(self, suffix: str = "desktop"):
        return dmc.Stack([
            dmc.Text("Market Volume Filters Here.", size="lg")
        ])