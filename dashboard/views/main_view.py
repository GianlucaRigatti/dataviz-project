from dash import html

class MainView:

    def create_layout(self):
        return html.Div([
            html.H1("Welcome to the Dashboard"),
            html.P("This is the main view of the dashboard."),
        ])