import dash
from dash import callback, ctx, Input, Output, State
from views.main_view import MainView

class MainController:
    def __init__(self):
        self.nav_links = [
            {"label": "Overview", "href": "/", "icon": "tabler:layout-dashboard"},
            {"label": "Geo", "href": "/geo", "icon": "tabler:world"},
            {"label": "Market Volume", "href": "/market-volume", "icon": "tabler:chart-bar"},
            {"label": "About", "href": "/about", "icon": "tabler:users"},
        ]

        self.view = MainView(self.nav_links)

    def layout(self):
        return self.view.build()

    @staticmethod
    @callback(
        Output("nav-drawer", "opened"),
        Output("nav-burger", "opened"),
        Input("nav-burger", "opened"),
        Input("nav-drawer", "opened"),
        prevent_initial_call=True,
    )
    def sync_nav_drawer(burger_opened, drawer_opened):
        trigger = ctx.triggered_id
        if trigger == "nav-burger":
            return burger_opened, burger_opened
        elif trigger == "nav-drawer":
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