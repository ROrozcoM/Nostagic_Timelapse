import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_leaflet as dl
import pytz
import owslib
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.fes import PropertyIsEqualTo, FilterRequest,  PropertyIsLessThanOrEqualTo, PropertyIsGreaterThanOrEqualTo, PropertyIsBetween
from owslib.etree import etree
from PIL import Image, ImageDraw
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


mapbox_url = "https://api.mapbox.com/styles/v1/{user}/{id}/tiles/{{z}}/{{x}}/{{y}}@2x?access_token={access_token}"
def generate_map(latitude=37.859836595170066, longitude=-4.796388111895123):
    mapa = dl.Map([
        dl.LayersControl([
            dl.BaseLayer(dl.TileLayer(),name='Base', checked=True),
            dl.Overlay(dl.WMSTileLayer(url="http://www.ign.es/wms-inspire/pnoa-ma", id='pnoa_wsm',
                                       layers="OI.OrthoimageCoverage", format="image/png", transparent=True,attribution='&copy; <a href="http://www.ign.es/">PNOA</a>'),
                       name='PNOA', checked=False),
            ]),
        #dl.Marker(id='farm-marker', position=[latitude, longitude]),
        dl.FeatureGroup(
            [
                dl.EditControl(
                    id="edit-sector-control",
                    draw={
                        "polyline": False,
                        "polygon": True,
                        "circle": False,
                        "circlemarker": False,
                        "rectangle": False,
                        "marker": False
                    },
                ),
            ]
        ),
    ],
        center=[latitude, longitude],
        style={"width": "100%", "height": "700px","borderRadius": "20px", "border": "2px solid #ccc", "zIndex": "1"},
        zoom=15,
        maxZoom=28,
        zoomControl=False,
        id='farm-selector')


    return mapa


def is_image_black(image, threshold=0.95):
    """Determina si una imagen es mayoritariamente negra.

    Args:
        image (PIL.Image.Image): La imagen en formato PIL.
        threshold (float): Porcentaje mínimo de píxeles negros para considerar una imagen como negra.

    Returns:
        bool: True si la imagen es mayoritariamente negra, False en caso contrario.
    """
    # Convertir la imagen a escala de grises
    gray_image = image.convert('L')
    # Convertir la imagen a un array numpy
    np_image = np.array(gray_image)
    # Calcular el número de píxeles negros
    black_pixels = np.sum(np_image == 0)
    # Calcular el total de píxeles
    total_pixels = np_image.size
    # Calcular el porcentaje de píxeles negros
    black_pixel_ratio = black_pixels / total_pixels
    return black_pixel_ratio > threshold
def generate_images(bounds):
    wms_hist = WebMapService('http://www.ign.es/wms/pnoa-historico', version='1.1.1')
    wms_act = WebMapService('http://www.ign.es/wms-inspire/pnoa-ma', version='1.1.1')
    img_list = []

    layers = [
        'PNOA2019', 'PNOA2018', 'PNOA2017', 'PNOA2016', 'PNOA2015', 'PNOA2014', 'PNOA2013',
        'PNOA2012', 'PNOA2011', 'PNOA2010', 'PNOA2009', 'PNOA2008', 'PNOA2007', 'PNOA2006',
        'PNOA2005', 'PNOA2004', 'pnoa10_2018', 'pnoa10_2016', 'pnoa10_2013', 'pnoa10_2009',
        'pnoa10_2007', 'pnoa10_2008', 'CampoCartagena', 'SIGPAC', 'OLISTAT',
        'Nacional_1981-1986', 'Interministerial_1973-1986', 'AMS_1956-1957', 'infoVuelos'
    ]
    # Invertir el orden de las capas
    layers.reverse()

    for layer in layers:
        img_response = wms_hist.getmap(
            layers=[layer],
            size=[600, 400],
            srs='EPSG:25830',
            bbox=bounds,
            format='image/jpeg',
            transparent=True
        )
        img = Image.open(BytesIO(img_response.read()))

        if not is_image_black(img):
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            img_list.append((img_str, layer))

    img_act = wms_act.getmap(layers=['OI.OrthoimageCoverage'],
                             # styles=['default'],
                             size=[600, 400],
                             srs='EPSG:25830',
                             # bbox=(f_bounds['minx'].min(), f_bounds['maxx'].max(), f_bounds['miny'].min(), f_bounds['maxy'].max()),
                             bbox=bounds,
                             # bbox=(f_bounds[0], f_bounds[2], f_bounds[1], f_bounds[3]),
                             # size=img_size,
                             format='image/jpeg',
                             transparent=True
                             )
    img_2022 = Image.open(BytesIO(img_act.read()))
    if not is_image_black(img_2022):
        buffer = BytesIO()
        img_2022.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        img_list.append((img_str, '2022'))

    return img_list
