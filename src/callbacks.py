from dash import html, callback, Output, Input, dcc, State, no_update, ctx
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from .components import generate_map



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

@callback(
    Output('farm-marker', 'position'),
    Output("button-submit", "disabled"),
    Input('farm-selector', 'n_clicks'),
    State('farm-selector', 'clickData'),
    prevent_initial_call=True,
)
def update_marker(n_clicks, click_data):
    print(n_clicks, click_data)
    if n_clicks is None:
        # Prevent initial callback invocation
        raise PreventUpdate

    # Get the click event data
    return {'lat': click_data['latlng']['lat'], 'lng': click_data['latlng']['lng']}, False