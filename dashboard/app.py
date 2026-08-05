from dash import Dash
from settings.settings import get_settings
from controllers.main_controller import MainController

settings = get_settings()

app = Dash(__name__)

app.layout = MainController().layout()
app.title = settings.app_name

if __name__ == '__main__':
    app.run(
        host=settings.server.host,
        port=settings.server.port,
        debug=settings.debug
    )