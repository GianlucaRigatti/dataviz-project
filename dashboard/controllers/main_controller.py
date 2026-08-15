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
            Output("main-content-container", "children"),
            Output("filters-controls-desktop", "children"),
            Output("filters-controls-mobile", "children"),
            Output("desktop-nav-tabs", "value"),
            Output("mobile-nav-segmented", "value"),
            Input("url", "pathname"),
            Input("desktop-nav-tabs", "value"),
            Input("mobile-nav-segmented", "value"),
        )
        def sync_navigation_and_render(url_path, desktop_val, mobile_val):
            trigger = ctx.triggered_id

            if trigger == "desktop-nav-tabs":
                target_path = desktop_val
            elif trigger == "mobile-nav-segmented":
                target_path = mobile_val
            else:
                target_path = url_path if url_path else "/"

            controller = self.pages.get(target_path, self.pages["/"])
            content_layout, filters_desktop, filters_mobile = controller.get_layouts()
            
            new_url = target_path if trigger in ["desktop-nav-tabs", "mobile-nav-segmented"] else dash.no_update
            new_desktop = target_path if desktop_val != target_path else dash.no_update
            new_mobile = target_path if mobile_val != target_path else dash.no_update

            return new_url, content_layout, filters_desktop, filters_mobile, new_desktop, new_mobile

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