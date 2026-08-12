import dash_mantine_components as dmc
from views.market_volume_view import MarketVolumeView

class MarketVolumeController:
    def __init__(self):
        self.view = MarketVolumeView()

    def get_layouts(self) -> tuple[dmc.Stack, dmc.Stack]:
        content = self.view.render_content()
        filters_desktop = self.view.render_filters(suffix="desktop")
        filters_mobile = self.view.render_filters(suffix="mobile")

        return content, filters_desktop, filters_mobile