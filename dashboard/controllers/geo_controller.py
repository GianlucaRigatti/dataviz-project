import dash_mantine_components as dmc
from views.geo_view import GeoView

class GeoController:
    def __init__(self):
        self.view = GeoView()

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack]:
        return self.view.render_content(), self.view.render_filters()