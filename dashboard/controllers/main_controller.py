import dash
from dash import callback, clientside_callback, ctx, Input, Output, State
from controllers.overview_controller import OverviewController
from controllers.geo_controller import GeoController
from controllers.volume_controller import VolumeController
from views.main_view import MainView


class MainController:
    def __init__(self):
        self.pages = {
            "/": OverviewController(),
            "/geo": GeoController(),
            "/volume": VolumeController(),
        }

        self.nav_links = [
            {"label": "Overview", "href": "/", "icon": "tabler:trending-up-down"},
            {"label": "Geo", "href": "/geo", "icon": "tabler:world"},
            {"label": "Volume", "href": "/volume", "icon": "tabler:car"},
        ]
        self.view = MainView(self.nav_links)
        self._register_callbacks()

    def get_layout(self):
        return self.view.build()

    def _register_callbacks(self):
        @callback(
            Output("url", "pathname"),
            Input("desktop-nav-tabs", "value"),
            Input("mobile-nav-segmented", "value"),
            State("url", "pathname"),
            prevent_initial_call=True,
        )
        def navigate_on_segment_change(desktop_val, mobile_val, current_path):
            trigger = ctx.triggered_id
            
            selected_path = desktop_val if trigger == "desktop-nav-tabs" else mobile_val

            if selected_path and selected_path != current_path:
                return selected_path
            return dash.no_update

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

    clientside_callback(
        """
        function(id) {
            // Prevent adding multiple event listeners if the component re-renders
            if (!window.navListenerAdded) {
                window.navListenerAdded = true;
                let lastScrollTop = 0;
                
                window.addEventListener("scroll", function() {
                    let st = window.pageYOffset || document.documentElement.scrollTop;
                    let nav = document.getElementById(id);
                    
                    if (nav) {
                        if (st > lastScrollTop && st > 50) {
                            // Scrolling DOWN: Slide it out of view (150% downwards)
                            nav.style.transform = "translate(-50%, 150%)";
                        } else {
                            // Scrolling UP: Bring it back to original position
                            nav.style.transform = "translate(-50%, 0)";
                        }
                    }
                    lastScrollTop = st <= 0 ? 0 : st; 
                }, false);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("mobile-bottom-nav", "id"),
        Input("mobile-bottom-nav", "id")
    )