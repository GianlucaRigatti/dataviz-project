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
            dmc.Drawer(
                id="nav-drawer",
                title=dmc.Group(
                    [
                        DashIconify(icon="tabler:menu-2", width=20),
                        dmc.Text("Pages", size="lg"),
                    ]
                ),
                position="left",
                size="80%",
                styles={
                    "content": {"display": "flex", "flexDirection": "column"},
                    "body": {"flex": 1, "display": "flex", "flexDirection": "column"},
                },
                children=dmc.Stack(
                    [
                        dmc.Stack(self.render_nav_links(mobile=True), mt="sm"),
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
                                ),
                                dmc.ColorSchemeToggle(
                                    lightIcon=DashIconify(icon="tabler:sun", width=20),
                                    darkIcon=DashIconify(icon="tabler:moon-stars", width=20),
                                    variant="light",
                                    color="yellow.6",
                                    size="lg",
                                ),
                            ],
                            gap="xs"
                        ),
                    ],
                    justify="space-between",
                    flex=1
                ),
            ),

            # filters-controls-mobile
            dmc.Drawer(
                id="filters-drawer",
                title=dmc.Group(
                    [
                        DashIconify(icon="tabler:filter", width=20),
                        dmc.Text("Filters", size="lg"),
                    ]
                ),
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
                                        size="sm"
                                    ),
                                    dmc.Group(
                                        [
                                            DashIconify(
                                                icon="tabler:layout-dashboard",
                                                width=24,
                                            ),
                                            dmc.Text(self.settings.app_name, size="xl"),
                                        ],
                                        gap="xs",
                                    )
                                ]),

                                dmc.Group(
                                    [
                                        dmc.Group([
                                            dmc.Group(
                                                self.render_nav_links(mobile=False),
                                                gap="xs",
                                                visibleFrom="md",
                                            ),
                                            dmc.ActionIcon(
                                                DashIconify(icon="tabler:filter", width=24),
                                                id="filters-toggle-btn",
                                                variant="filled",
                                                color="blue.6",
                                                hiddenFrom="md",
                                                size="lg",
                                            )
                                        ]),

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
                                    gap="lg"
                                ),
                            ]
                        )
                    ),

                    # filters-controls-desktop
                    dmc.AppShellAside(
                        p="md",
                        visibleFrom="md",
                        children=dmc.Stack(id="filters-controls-desktop")
                    ),

                    # main-content-container
                    dmc.AppShellMain(
                        children=dmc.Box(id="main-content-container", p="md")
                    )

                ]
            )

        ])

    def render_nav_links(self, mobile, color="blue.6") -> list[dmc.Anchor]:
        match mobile:
            case True:
                return [
                    dmc.Anchor(
                        dmc.Group(
                            [
                                DashIconify(icon=link["icon"], width=20),
                                dmc.Text(link["label"], size="lg"),
                            ],
                            gap="xs",
                            align="center",
                        ),
                        href=link["href"],
                        underline=False,
                        c=color,
                    ) for link in self.nav_links
                ]
            case False:
                return [
                    dmc.Anchor(
                        dmc.Button(
                            link["label"],
                            leftSection=DashIconify(icon=link["icon"], width=20),
                            # variant="subtle", has no glow only hover
                            variant="light",
                            color=color,
                            fullWidth=True,
                            justify="start",
                            px="xs",
                        ),
                        href=link["href"],
                        underline=False,
                    )
                    for link in self.nav_links
                ]