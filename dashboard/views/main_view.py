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
                header={"height": {"base": 60, "md": 60}},
                aside={"width": 350, "breakpoint": "md", "collapsed": {"mobile": True}},
                children=[
                    dmc.AppShellHeader(
                        bg="light-dark(var(--mantine-color-white), #283044)",
                        children=dmc.Group(
                            justify="space-between",
                            h="100%",
                            px="md",
                            children=[
                                dmc.Group([
                                    DashIconify(icon="tabler:template-filled", height=36, color="var(--mantine-color-blue-3)"),
                                    dmc.Title(self.settings.app_name, order=2, fw=800, display={"base": "none", "sm": "block"}),
                                    dmc.Title(self.settings.short_app_name, order=2, fw=800, display={"base": "block", "sm": "none"}),
                                ], align="center", gap="sm"),

                                dmc.Group(
                                    [
                                        self.render_nav_links(mobile=False),
                                        
                                        # Mobile Filters Popover
                                        dmc.Popover(
                                            [
                                                dmc.PopoverTarget(
                                                    dmc.ActionIcon(
                                                        DashIconify(icon="tabler:filter", width=20),
                                                        id="filters-toggle-btn",
                                                        variant="filled",
                                                        color="blue.6",
                                                        hiddenFrom="md",
                                                        size="lg",
                                                    )
                                                ),
                                                dmc.PopoverDropdown(
                                                    dmc.Stack(id="filters-controls-mobile"),
                                                    style={
                                                        "backgroundColor": "light-dark(white, var(--mantine-color-dark-8))",
                                                    },
                                                    p="xs",
                                                    pt="lg",
                                                    pb="lg",
                                                ),
                                            ],
                                            position="bottom",
                                            withArrow=True,
                                            shadow="lg",
                                            width=250,
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
                                                    id="color-scheme-switch",
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
                        children=[
                            dmc.Box(
                                id="main-content-container", 
                                p={"base": "lg", "md": "xl"}
                            ),
                            dmc.Space(h="15vh") 
                        ]
                    ),
                ],
            ),

            # Mobile Bottom Navigation Bar
            dmc.Affix(
                id="mobile-bottom-nav",
                hiddenFrom="md",
                position={"bottom": "md", "left": "50%"},
                style={
                    "transform": "translate(-50%, 0)", 
                    "transition": "transform 0.3s ease",
                    "width": "90%", 
                    "maxWidth": "400px"
                },
                zIndex=100,
                children=dmc.Paper(
                    shadow="lg",
                    withBorder=True,
                    children=self.render_nav_links(mobile=True)
                )
            )
        ])

    def render_nav_links(self, mobile: bool, current_path: str = "/"):
        if mobile:
            return dmc.SegmentedControl(
                id="mobile-nav-segmented",
                value=current_path,
                size="md",
                fullWidth=True,
                color="blue.6",
                data=[
                    {
                        "label": dmc.Center([
                            DashIconify(icon=link["icon"], width=20),
                            dmc.Text(link["label"], ml="xs", size="sm"),
                        ]),
                        "value": link["href"]
                    }
                    for link in self.nav_links
                ],
            )
        else:
            return dmc.Tabs(
                id="desktop-nav-tabs",
                value=current_path,
                orientation="horizontal",
                variant="pills",
                color="blue.6",
                visibleFrom="md",
                children=[
                    dmc.TabsList(
                        children=[
                            dmc.TabsTab(
                                dmc.Text(link["label"], size="sm"),
                                value=link["href"],
                                leftSection=DashIconify(icon=link["icon"], width=20),
                                p="sm",
                            )
                            for link in self.nav_links
                        ],
                    )
                ],
            )