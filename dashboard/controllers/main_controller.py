from views.main_view import MainView

class MainController:
    def __init__(self):
        self.view = MainView()

    def layout(self):
        return self.view.create_layout()