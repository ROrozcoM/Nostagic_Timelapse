import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, dcc, callback, Input, Output, State, html
from components import generate_map, generate_images, make_card
from shapely.geometry import shape
from pyproj import Transformer
from dash_iconify import DashIconify
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

app = Dash(__name__,external_stylesheets=dmc.styles.ALL)
server = app.server
app.title='Nostalgic Visualizator'


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
                            dmc.Title("Nostalgic Visualizator", order=2),
                        ],
                        justify="center",
                        align="stretch",
                        style={'textAlign': 'center'}
                    ),
                ],
                inheritPadding=True,
                py="xs",
                ),
                html.Br(),
                dmc.List(
                    size="sm",
                    spacing="sm",
                    children=[
                        dmc.ListItem(
                            "Busca región de interés en el mapa",
                            icon=dmc.ThemeIcon("1", radius="xl", color="teal", size=20)
                        ),
                        dmc.ListItem(
                            [
                                html.Span("Puedes cambiar el tipo de mapa pulsando "),
                                html.Span(dmc.Kbd("Layers")),
                            ],
                            icon=dmc.ThemeIcon("*", radius="xl", color="orange", size=18),
                            style={'fontSize': '10px'}
                        ),
                        dmc.ListItem(
                            [
                                html.Span("Selecciona tu región de interés pulsando "),
                                html.Span(dmc.Kbd("⬠")),
                                html.Span(" y dibujando el trazado"),
                            ],
                            icon=dmc.ThemeIcon("2", radius="xl", color="teal", size=20)
                        ),
                        dmc.ListItem(
                            [
                                html.Span("Completa el polígono con el punto de inicio y pulsa "),
                                html.Span(dmc.Kbd("Aceptar")),
                            ],
                            icon=dmc.ThemeIcon("3", radius="xl", color="teal", size=20)
                        ),
                    ],
                    style={'fontSize': '12px'}
                ),
                html.Br(),
                dmc.CardSection([
                    dmc.Grid(
                        children=[
                            dmc.Button("Aceptar", id="button-submit-sector", disabled=False),
                            dmc.Space(w=20),
                            dcc.Location(id='url-refresh', refresh=True),
                            dmc.Button("Refrescar", id="button-cancel"),
                        ],
                        justify="center",
                        align="stretch",
                        gutter="xl",
                    ),
                ],
                inheritPadding=True,
                py="xs",
                ),

                # DCC Store para manejar el estado del mapa
                dcc.Store(id='map-visible', data=True),  # Por defecto el mapa es visible

                dmc.CardSection([
                    dmc.Grid(
                        children=[
                            dmc.GridCol(html.Div(id='new-coordinates-content'), span=6),
                            dcc.Store(id="new_sector-template"),
                        ],
                        justify="center",
                        align="stretch",
                        gutter="xl",
                    ),
                ],
                withBorder=True,
                py="xs",
                ),

                dmc.CardSection([
                    dmc.Grid(
                        children=[
                            dmc.GridCol(id='map-content', children=generate_map(), span='auto'),  # Mostrar el mapa inicialmente
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
        dmc.Card(
            dcc.Loading(html.Div(id="dummy-output")),  # Contenido a mostrar después de pulsar Aceptar
            withBorder=True,
            shadow="sm",
            radius="md",
            style={"display": "flex",
                   "justifyContent": "center",
                   "alignItems": "center",}
        ),
    ],
    id="mantine-provider",
    forceColorScheme="light",
)

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

        # Wrap slides in a Carousel component
        carousel = dmc.Carousel(
            children=[dmc.CarouselSlide(make_card(img_src, layer_name)) for img_src, layer_name in img_list],
            id="carousel-drag-free",
            withIndicators=True,
            height=300,
            dragFree=True,
            slideGap="md",
            loop=True,
            align="start",
            style={"maxWidth": "800px", "margin": "0 auto"},
        )

        return html.Div(carousel)
    else:
        return "No bounds received or the button was not clicked."

@callback(
    Output('url-refresh', 'href'),
    Input('button-cancel', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_page(n_clicks):
    if n_clicks:
        return '/'  # Recarga la página actual

@callback(
    Output('map-visible', 'data'),
    Output('map-content', 'children'),
    Input('button-submit-sector', 'n_clicks'),
    prevent_initial_call=True
)
def update_map(n_clicks):
    # Cambia el estado para ocultar el mapa y mostrar el contenido de carga
    return False, dcc.Loading(html.Div(id="dummy-output"))


if __name__ == "__main__":
    app.run_server(debug=True)