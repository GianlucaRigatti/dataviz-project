from dash import dcc
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from settings.settings import get_settings


class MainView:
    def __init__(self, nav_links):
        self.nav_links = nav_links
        self.settings = get_settings()

    def build(self):
        return dmc.Box([
            dcc.Location(id="url", refresh=False),

            dmc.AppShell(
                id="app-shell",
                header={"height": 60},
                footer={"height": 65},
                aside={"width": 300, "breakpoint": "md", "collapsed": {"mobile": True}},
                children=[
                    dmc.AppShellHeader(
                        dmc.Group(
                            justify="space-between",
                            h="100%",
                            px="md",
                            children=[
                                dmc.Group([
                                    dmc.Text(self.settings.app_name, size="xl", fw=700),
                                ]),

                                dmc.Group(
                                    [
                                        self.render_nav_links(mobile=False),
                                        
                                        # Mobile Filters Popover
                                        dmc.Popover(
                                            [
                                                dmc.PopoverTarget(
                                                    dmc.ActionIcon(
                                                        DashIconify(icon="tabler:filter", width=24),
                                                        id="filters-toggle-btn",
                                                        variant="filled",
                                                        color="blue.6",
                                                        hiddenFrom="md",
                                                        size="lg",
                                                    )
                                                ),
                                                dmc.PopoverDropdown(
                                                    dmc.Stack(id="filters-controls-mobile"),
                                                ),
                                            ],
                                            position="bottom",
                                            withArrow=True,
                                            shadow="md",
                                        ),
                                        
                                        # GitHub and Theme toggles
                                        dmc.Group(
                                            [
                                                dmc.Anchor(
                                                    dmc.ActionIcon(
                                                        DashIconify(icon="tabler:brand-github", width=20),
                                                        variant="light",
                                                        color="grape.6",
                                                        size="lg",
                                                    ),
                                                    href="https://github.com/GianlucaRigatti/dataviz-project",
                                                    underline=False,
                                                    target="_blank",
                                                ),
                                                dmc.ColorSchemeToggle(
                                                    lightIcon=DashIconify(icon="tabler:sun", width=20),
                                                    darkIcon=DashIconify(icon="tabler:moon-stars", width=20),
                                                    variant="light",
                                                    color="yellow.6",
                                                    size="lg",
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                    gap="md",
                                ),
                            ],
                        )
                    ),

                    # Mobile Bottom Navigation Bar
                    dmc.AppShellFooter(
                        p="xs",
                        hiddenFrom="md",
                        zIndex=100,
                        withBorder=True,
                        children=self.render_nav_links(mobile=True)
                    ),

                    # Desktop Aside Filters
                    dmc.AppShellAside(
                        p="md",
                        visibleFrom="md",
                        children=dmc.Stack([
                            dmc.Group([
                                DashIconify(icon="tabler:filter", width=20),
                                dmc.Text("Filters", size="lg", fw=500),
                            ]),
                            dmc.Stack(id="filters-controls-desktop"),
                        ])
                    ),

                    # Main Content Area
                    dmc.AppShellMain(
                        children=dmc.Box(id="main-content-container", p="md")
                    ),
                ],
            ),
        ])

    def render_nav_links(self, mobile: bool, current_path: str = "/"):
        match mobile:
            case True:
                control_id = "mobile-nav-tabs"
                orientation = "horizontal" 
                visible_from = None
                grow = True 
                text_size = "xs"
                full_w = "100%"
            case False:
                control_id = "desktop-nav-tabs"
                orientation = "horizontal"
                visible_from = "md"
                grow = False
                text_size = "sm"
                full_w = None

        return dmc.Tabs(
            id=control_id,
            value=current_path,
            orientation=orientation,
            variant="pills",
            visibleFrom=visible_from,
            w=full_w,
            children=[
                dmc.TabsList(
                    grow=grow,
                    w=full_w,
                    children=[
                        dmc.TabsTab(
                            dmc.Text(link["label"], size=text_size),
                            value=link["href"],
                            leftSection=DashIconify(icon=link["icon"], width=18),
                            w=full_w if not mobile else None,
                        )
                        for link in self.nav_links
                    ],
                )
            ],
        )