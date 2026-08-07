import dash
from dash import Dash, html, callback, Output, Input, State, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify

app = Dash(__name__)

nav_links = [
    {"label": "Overview", "href": "/", "icon": "tabler:layout-dashboard"},
    {"label": "Geo", "href": "/geo", "icon": "tabler:world"},
    {"label": "Market Volume", "href": "/market-volume", "icon": "tabler:chart-bar"},
    {"label": "About", "href": "/about", "icon": "tabler:users"},
]

# Reusable list of filter components
filter_controls = [
    dmc.Text("Plot Filters", fw=500, mb="md"),
    dmc.Select(label="Select Region", data=["North", "South", "East", "West"], value="North", mb="sm"),
    dmc.RangeSlider(label="Date Range", min=0, max=100, value=[20, 80], mb="xl"),
    dmc.Button("Apply Filters", fullWidth=True),
]

def render_nav_links(nav_links, size="lg", color="dimmed") -> dmc.Stack:
    return dmc.Stack(
        [
            dmc.Anchor(
                dmc.Group(
                    [
                        DashIconify(icon=link["icon"], width=20 if size == "lg" else 18),
                        dmc.Text(link["label"], size=size),
                    ],
                    gap="xs",
                    align="center",
                ),
                href=link["href"],
                underline=False,
                c=color,
            ) for link in nav_links
        ]
    )

app.layout = dmc.MantineProvider(
    html.Div([
        # 1. Left Navigation Drawer (Mobile)
        dmc.Drawer(
            id="nav-drawer",
            position="left",
            size="80%",
            children=render_nav_links(nav_links)
        ),
        
        # 2. Right Filter Drawer (Mobile - partial width control via 'size')
        dmc.Drawer(
            id="filter-drawer",
            title=dmc.Group(
                [
                    DashIconify(icon="tabler:filter", width=20),
                    dmc.Text("Filters", size="lg"),
                ]
            ),
            position="right",
            size="80%",
            children=dmc.Stack([
                dmc.Text("Filter Controls Here", size="lg")
            ]),
        ),

        dmc.AppShell(
            [
                dmc.AppShellHeader(
                    dmc.Group(
                        justify="space-between",
                        h="100%",
                        px="md",
                        children=[
                            # LEFT SIDE: Nav Burger + Title
                            dmc.Group([
                                dmc.Burger(id="nav-burger", opened=False, hiddenFrom="md", size="sm"),
                                dmc.Text("My Dashboard", size="xl", fw=700),
                            ]),
                            
                            # RIGHT SIDE: Desktop Links + Filter ActionIcon
                            dmc.Group([
                                dmc.Group(
                                    [dmc.Anchor(link["label"], href=link["href"], underline=False) for link in nav_links],
                                    visibleFrom="md",
                                ),
                                dmc.ActionIcon(
                                    DashIconify(icon="tabler:filter", width=24),
                                    id="filter-toggle-btn",
                                    hiddenFrom="md",
                                    size="lg",
                                    variant="subtle",
                                    color="gray",
                                ),
                            ])
                        ]
                    )
                ),
                
                # Desktop Filter Sidebar (hidden on mobile, drawer takes over)
                dmc.AppShellAside(
                    p="md",
                    visibleFrom="md",
                    children=filter_controls,
                ),
                
                dmc.AppShellMain(
                    children=[
                        dmc.Title("Dashboard Content", order=2),
                        dmc.Text("Shrink the screen. The filter button opens a right-aligned drawer taking only 320px width.", mt="md"),
                    ]
                )
            ],
            header={"height": 60},
            aside={"width": 300, "breakpoint": "md", "collapsed": {"mobile": True}},
            id="app-shell",
        )
    ])
)

# Callback 1: Open/Close the Right Filter Drawer on mobile
@callback(
    Output("filter-drawer", "opened"),
    Input("filter-toggle-btn", "n_clicks"),
    State("filter-drawer", "opened"),
    prevent_initial_call=True,
)
def toggle_filter_drawer(n_clicks, is_opened):
    return not is_opened

# Callback 2: Open/Close the Left Navigation Drawer on mobile
@callback(
    Output("nav-drawer", "opened"),
    Output("nav-burger", "opened"),
    Input("nav-burger", "opened"),
    Input("nav-drawer", "opened"),
    prevent_initial_call=True,
)
def sync_nav_drawer(burger_opened, drawer_opened):
    trigger = ctx.triggered_id
    if trigger == "nav-burger":
        return burger_opened, burger_opened
    elif trigger == "nav-drawer":
        return drawer_opened, drawer_opened
    return dash.no_update, dash.no_update

if __name__ == "__main__":
    app.run(debug=True)