import dash
from dash import callback, ctx, Input, Output, State
from controllers.overview_controller import OverviewController
from controllers.geo_controller import GeoController
from controllers.market_volume_controller import MarketVolumeController
from views.main_view import MainView

class MainController:

    PAGE_MAP = {
        "/": OverviewController,
        "/geo": GeoController,
        "/market-volume": MarketVolumeController,
    }

    def __init__(self):
        self.nav_links = [
            {"label": "Overview", "href": "/", "icon": "tabler:trending-up-down"},
            {"label": "Geo", "href": "/geo", "icon": "tabler:world"},
            {"label": "Market Volume", "href": "/market-volume", "icon": "tabler:car"}
        ]
        self.view = MainView(self.nav_links)

    def get_layout(self):
        return self.view.build()

    @staticmethod
    @callback(
        Output("main-content-container", "children"),
        Output("filters-controls-desktop", "children"),
        Output("filters-controls-mobile", "children"),
        Input("url", "pathname"),
    )
    def render_page_content(pathname):
        controller_cls = MainController.PAGE_MAP.get(pathname, MainController.PAGE_MAP["/"])
        controller = controller_cls()
        content_layout, filter_layout = controller.get_layouts()
        return content_layout, filter_layout, filter_layout

    @staticmethod
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

    @staticmethod
    @callback(
        Output("filters-drawer", "opened"),
        Input("filters-toggle-btn", "n_clicks"),
        State("filters-drawer", "opened"),
        prevent_initial_call=True,
    )
    def toggle_filter_drawer(_, is_opened):
        return not is_opened