from dash import html, callback, Output, Input, dcc, State, no_update, ctx
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from .components import generate_map, generate_images
import dash_bootstrap_components as dbc
from shapely.geometry import shape
import json
from dash.exceptions import PreventUpdate
from pyproj import Transformer



@callback(
    Output('new-coordinates-content', 'children'),
    Input('url', 'pathname'),
)
def generate_layout(pathname):
    layout = [
        dmc.SimpleGrid(cols=2, children=[
            dmc.Stack(children=[dmc.TextInput(label="Farm name", id='farm-name', required=True),
                                dmc.TextInput(label="Description", id='farm-description'),
                                ]),
            generate_map(),

        ]),


        dmc.Button("Accept", id="button-submit", disabled=True),
        dmc.Button("Cancel", id="button-cancel"),

    ]
    return layout

