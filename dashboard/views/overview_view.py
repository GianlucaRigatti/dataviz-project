import dash_mantine_components as dmc

class OverviewView:
    def render_content(self):
        return dmc.Stack([
            dmc.Text("Overview Content Here.", size="lg")
        ])

    def render_filters(self):
        return dmc.Stack([
            dmc.Text("Overview Filters Here.", size="lg")
        ])