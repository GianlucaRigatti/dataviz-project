import dash_mantine_components as dmc
from views.overview_view import OverviewView

class OverviewController:
    def __init__(self):
        self.view = OverviewView()

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack]:
        return self.view.render_content(), self.view.render_filters()

    # TODO: Add callbacks here to populate the cards with the actual content (charts, filters, etc.).