import dash_mantine_components as dmc

class GeoView:
    def render_content(self):
        return dmc.Stack([
            dmc.Text("Geo Content Here.", size="lg")
        ])

    def render_filters(self):
        return dmc.Stack([
            dmc.Text("Geo Filters Here.", size="lg")
        ])