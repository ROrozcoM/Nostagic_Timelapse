import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import Dash, _dash_renderer, dcc, callback, Input, Output, State, clientside_callback, html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from components import generate_map, generate_images
from shapely.geometry import shape
import json
from dash.exceptions import PreventUpdate
from pyproj import Transformer
import dash_bootstrap_components as dbc




_dash_renderer._set_react_version("18.2.0")


stylesheets = [
    "https://unpkg.com/@mantine/dates@7/styles.css",
    "https://unpkg.com/@mantine/code-highlight@7/styles.css",
    "https://unpkg.com/@mantine/charts@7/styles.css",
    "https://unpkg.com/@mantine/carousel@7/styles.css",
    "https://unpkg.com/@mantine/notifications@7/styles.css",
    "https://unpkg.com/@mantine/nprogress@7/styles.css",
]

app = Dash(external_stylesheets=stylesheets)



style = {
    "border": f"1px solid {dmc.DEFAULT_THEME['colors']['indigo'][4]}",
    "textAlign": "center",
}

app.layout = dmc.MantineProvider(
    [
            dmc.Card(
                children=[
                    html.Br(),
                    dmc.CardSection([
                        dmc.Grid(
                            children=[
                                dmc.Title("Visualizador de evolución temporal", order=1),
                            ],
                            justify="center",
                            align="stretch",
                            gutter="xl",
                        ),
                    ],
                    #withBorder=True,
                    inheritPadding=True,
                    py="xs",
                    ),
                    html.Br(),
                    dmc.Stepper(
                        style={"marginLeft": "20%", "marginRight": "20%"},
                        active=1,
                        children=[
                            dmc.StepperStep(
                                label="Paso 1",
                                description="Busca región de interés",
                            ),
                            dmc.StepperStep(
                                label="Paso 2",
                                description="Selecciona región de interés",
                                children=dmc.Text(
                                    "Usa el icono del pentágono que aparece en el mapa y completa un polígono cerrado",
                                    ta="center"),
                            ),
                            dmc.StepperStep(
                                label="Paso 3",
                                description="Pulsa Aceptar",
                            ),

                        ],
                    ),
                    html.Br(),
                    dmc.CardSection([
                        dmc.Grid(
                            children=[
                                dmc.Button("Aceptar", id="button-submit-sector", disabled=True),
                                dmc.Space(w=20),
                                dcc.Location(id='url-refresh', refresh=True),
                                dmc.Button("Cancelar", id="button-cancel"),
                            ],
                            justify="center",
                            align="stretch",
                            gutter="xl",
                        ),
                    ],
                    #withBorder=True,
                    inheritPadding=True,
                    py="xs",
                    ),

                    dmc.CardSection([
                        dmc.Grid(
                            children=[
                                dmc.GridCol(html.Div(id='new-coordinates-content'),span=6),
                                dcc.Store(id="new_sector-template"),
                            ],
                            justify="center",
                            align="stretch",
                            gutter="xl",
                        ),
                    ],
                        withBorder=True,
                        #inheritPadding=True,
                        py="xs",
                    ),

                    dmc.CardSection([
                        dmc.Grid(
                            children=[
                                dmc.GridCol(generate_map(),span=5),
                                dmc.GridCol(
                                    dmc.Card(
                                    dcc.Loading(html.Div(id="dummy-output")),
                                    withBorder=True,
                                    shadow="sm",
                                    radius="md",
                                    style={"display": "flex",
                                           "justifyContent": "center",
                                           "alignItems": "center",}
                                    ),
                                span='auto'),
                            ],
                            justify="center",
                            align="stretch",
                            gutter="xl",
                        ),
                    ],
                        withBorder=True,
                        inheritPadding=True,
                        py="xs",
                    ),
                ],
                withBorder=True,
                shadow="sm",
                radius="md",

            ),
            ],
    id="mantine-provider",
    forceColorScheme="light",
)

# @callback(
#     Output('farm-marker', 'position'),
#     Output("button-submit", "disabled"),
#     Input('farm-selector', 'n_clicks'),
#     State('farm-selector', 'clickData'),
#     prevent_initial_call=True,
# )
# def update_marker(n_clicks, click_data):
#     print(n_clicks, click_data)
#     if n_clicks is None:
#         # Prevent initial callback invocation
#         raise PreventUpdate
#
#     # Get the click event data
#     return {'lat': click_data['latlng']['lat'], 'lng': click_data['latlng']['lng']}, False

@callback(
    Output("button-submit-sector", "disabled"),
    Output("new_sector-template", "data"),
    Input("edit-sector-control", "geojson"),
    prevent_initial_call=True
)
def enable_submit(geojson):
    if geojson is None or len(geojson['features']) == 0:
        return True, None
    # Extraer la geometría del polígono
    polygon = shape(geojson['features'][0]['geometry'])
    # Calcular los bounds del polígono (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = polygon.bounds
    # Crear un diccionario con los bounds
    # Transformar los bounds a EPSG:25830 (asumiendo que las coordenadas originales están en EPSG:4326)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
    minx, miny = transformer.transform(minx, miny)
    maxx, maxy = transformer.transform(maxx, maxy)

    # Crear un diccionario con los bounds en EPSG:25830
    bounds = [minx, miny, maxx, maxy]
    print("Bounds del polígono en EPSG:25830:", bounds)
    return False, bounds
@callback(
    Output("dummy-output", "children"),  # Salida ficticia
    Input("button-submit-sector", "n_clicks"),  # Botón que dispara la acción
    State("new_sector-template", "data"),  # Bounds del polígono
    prevent_initial_call=True
)
def update_output(n_clicks, bounds):
    if n_clicks is not None and bounds:
        img_list = generate_images(bounds)

        # Crear los items para el carrusel
        carousel_items = [
            {
                "key": str(i),
                "src": f"data:image/jpeg;base64,{img_src}",
                "header": layer_name,
                "caption": "Ortofoto",
            }
            for i, (img_src, layer_name) in enumerate(img_list)
        ]

        # Crear el carrusel usando los items generados
        carousel = dbc.Carousel(
            items=carousel_items,
            controls=True,
            indicators=True,
            ride='carousel',
        )

        return carousel
    else:
        return "No se recibieron bounds o no se ha hecho clic en el botón."

@callback(
    Output('url-refresh', 'href'),
    Input('button-cancel', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_page(n_clicks):
    if n_clicks:
        return '/'  # Recarga la página actual

if __name__ == "__main__":
    app.run_server(debug=True)