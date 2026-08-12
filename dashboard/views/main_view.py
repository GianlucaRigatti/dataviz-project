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
            
            # Mobile Navigation Drawer
            dmc.Drawer(
                id="nav-drawer",
                title=dmc.Group([
                    DashIconify(icon="tabler:menu-2", width=20),
                    dmc.Text("Pages", size="lg"),
                ]),
                position="left",
                size="80%",
                styles={
                    "content": {"display": "flex", "flexDirection": "column"},
                    "body": {"flex": 1, "display": "flex", "flexDirection": "column"},
                },
                children=dmc.Stack(
                    [
                        self.render_nav_links(mobile=True),
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
                    justify="space-between",
                    flex=1,
                    mt="sm",
                ),
            ),

            # Mobile Filters Drawer
            dmc.Drawer(
                id="filters-drawer",
                title=dmc.Group([
                    DashIconify(icon="tabler:filter", width=20),
                    dmc.Text("Filters", size="lg"),
                ]),
                position="right",
                size="80%",
                children=dmc.Stack(id="filters-controls-mobile"),
            ),

            dmc.AppShell(
                id="app-shell",
                header={"height": 60},
                aside={"width": 300, "breakpoint": "md", "collapsed": {"mobile": True}},
                children=[
                    dmc.AppShellHeader(
                        dmc.Group(
                            justify="space-between",
                            h="100%",
                            px="md",
                            children=[
                                dmc.Group([
                                    dmc.Burger(
                                        id="nav-burger",
                                        opened=False,
                                        hiddenFrom="md",
                                        size="sm",
                                    ),
                                    dmc.Text(self.settings.app_name, size="xl"),
                                ]),

                                dmc.Group(
                                    [
                                        self.render_nav_links(mobile=False),
                                        dmc.ActionIcon(
                                            DashIconify(icon="tabler:filter", width=24),
                                            id="filters-toggle-btn",
                                            variant="filled",
                                            color="blue.6",
                                            hiddenFrom="md",
                                            size="lg",
                                        ),
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
                                            visibleFrom="md",
                                            gap="xs",
                                        ),
                                    ],
                                    gap="md",
                                ),
                            ],
                        )
                    ),

                    # Desktop Aside Filters
                    dmc.AppShellAside(
                        p="md",
                        visibleFrom="md",
                        children=dmc.Stack([
                            dmc.Group([
                                DashIconify(icon="tabler:filter", width=20),
                                dmc.Text("Filters", size="lg"),
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
                orientation = "vertical"
                visible_from = None
                grow = True
                text_size = "md"
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
                            w=full_w,
                        )
                        for link in self.nav_links
                    ],
                )
            ],
        )