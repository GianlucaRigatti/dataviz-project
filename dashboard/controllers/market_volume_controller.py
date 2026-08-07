import dash_mantine_components as dmc
from views.market_volume_view import MarketVolumeView

class MarketVolumeController:
    def __init__(self):
        self.view = MarketVolumeView()

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack]:
        return self.view.render_content(), self.view.render_filters()