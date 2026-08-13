import dash_mantine_components as dmc
from dash import Dash
from settings.settings import get_settings
from controllers.main_controller import MainController

settings = get_settings()

app = Dash(
    __name__,
    external_stylesheets=[
        dmc.styles.ALL,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
    ],
    suppress_callback_exceptions=True
)

theme = {
    "defaultRadius": "lg",
    "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "colors": {
        "dark": [
            "#FFFFFF",
            "#F1F3F5",
            "#909296",
            "#5A6072",
            "#43495E",
            "#333C52",
            "#283044",
            "#202634",
            "#1A1E29",
            "#12151D",
        ],
        "gray": [
            "#F8F9FB",
            "#F3F5F7",
            "#ECEFF2",
            "#E1E5E9",
            "#CDD2D8",
            "#9299A3",
            "#707782",
            "#505660",
            "#292D33",
            "#111318",
        ],
    },
    "components": {
        "Card": {
            "defaultProps": {
                "withBorder": True,
            },
            "styles": {
                "root": {
                    "borderColor": "light-dark(var(--mantine-color-gray-3), var(--mantine-color-dark-9))",
                }
            },
        },
        "Paper": {
            "defaultProps": {
                "withBorder": True,
                "shadow": "lg",
            },
            "styles": {
                "root": {
                    "borderColor": "light-dark(var(--mantine-color-gray-3), var(--mantine-color-dark-9))",
                }
            },
        },
    },
}

main_controller = MainController()
app.layout = dmc.MantineProvider(main_controller.get_layout(), theme=theme, defaultColorScheme="dark")
app.title = settings.app_name

if __name__ == '__main__':
    app.run(
        host=settings.server.host,
        port=settings.server.port,
        debug=settings.debug
    )