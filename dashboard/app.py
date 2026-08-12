import dash_mantine_components as dmc
from dash import Dash
from settings.settings import get_settings
from controllers.main_controller import MainController

settings = get_settings()

app = Dash(
    __name__,
    external_stylesheets=dmc.styles.ALL,
    suppress_callback_exceptions=True
)

main_controller = MainController()
app.layout = dmc.MantineProvider(main_controller.get_layout(), theme={"defaultRadius": "xl"})
app.title = settings.app_name

if __name__ == '__main__':
    app.run(
        host=settings.server.host,
        port=settings.server.port,
        debug=settings.debug
    )