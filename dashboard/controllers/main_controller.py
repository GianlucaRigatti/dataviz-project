import dash
from dash import callback, ctx, Input, Output, State
from controllers.overview_controller import OverviewController
from controllers.geo_controller import GeoController
from controllers.market_volume_controller import MarketVolumeController
from views.main_view import MainView

class MainController:
    def __init__(self):
        # 1. Pre-instantiate page controllers at startup
        self.pages = {
            "/": OverviewController(),
            "/geo": GeoController(),
            "/market-volume": MarketVolumeController(),
        }

        self.nav_links = [
            {"label": "Overview", "href": "/", "icon": "tabler:trending-up-down"},
            {"label": "Geo", "href": "/geo", "icon": "tabler:world"},
            {"label": "Market Volume", "href": "/market-volume", "icon": "tabler:car"}
        ]
        self.view = MainView(self.nav_links)
        self._register_callbacks()

    def get_layout(self):
        return self.view.build()

    def _register_callbacks(self):
        @callback(
            Output("main-content-container", "children"),
            Output("filters-controls-desktop", "children"),
            Output("filters-controls-mobile", "children"),
            Input("url", "pathname"),
        )
        def render_page_content(pathname):
            controller = self.pages.get(pathname, self.pages["/"])
            content_layout, filters_desktop, filters_mobile = controller.get_layouts()
            return content_layout, filters_desktop, filters_mobile

        @callback(
            Output("nav-drawer", "opened"),
            Output("nav-burger", "opened"),
            Input("nav-burger", "opened"),
            Input("nav-drawer", "opened"),
            Input("url", "pathname"),
            prevent_initial_call=True,
        )
        def sync_nav_drawer(burger_opened, drawer_opened, _):
            trigger = ctx.triggered_id
            if trigger == "url":
                return False, False
            if trigger == "nav-burger":
                return burger_opened, burger_opened
            if trigger == "nav-drawer":
                return drawer_opened, drawer_opened
            return dash.no_update, dash.no_update

        @callback(
            Output("filters-drawer", "opened"),
            Input("filters-toggle-btn", "n_clicks"),
            State("filters-drawer", "opened"),
            prevent_initial_call=True,
        )
        def toggle_filter_drawer(_, is_opened):
            return not is_opened

        @callback(
            Output("url", "pathname"),
            Input("desktop-nav-segmented-control", "value"),
            prevent_initial_call=True
        )
        def navigate_on_segment_change(selected_href):
            return selected_href