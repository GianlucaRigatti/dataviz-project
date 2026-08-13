import dash_mantine_components as dmc

class VolumeView:
    def render_content(self):
        return dmc.Stack([
            dmc.Text("Volume Content Here.", size="lg")
        ])

    def render_filters(self, suffix: str = "desktop"):
        return dmc.Stack([
            dmc.Text("Volume Filters Here.", size="lg")
        ])