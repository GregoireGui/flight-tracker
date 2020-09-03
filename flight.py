import requests
from os import path
import pandas as pd
from functools import partial
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, ESRI_IMAGERY
from bokeh.models import HoverTool, LabelSet, ColumnDataSource

from utils import wgs84_to_web_mercator, wgs84_web_mercator_point

ICON_URL = 'https://image.flaticon.com/icons/svg/984/984233.svg'
BASE_URL = 'https://opensky-network.org/api'
LON_MIN, LAT_MIN = -125.974, 30.038
LON_MAX, LAT_MAX = 68.748, 52.214

# Get data for area
def get_data(lon_min=LON_MIN, lat_min=LAT_MIN, lon_max=LON_MAX, lat_max=LAT_MAX):
    url = f'{BASE_URL}/states/all?lamin={lat_min}&lomin={lon_min}&lamax={lat_max}&lomax={lon_max}'
    return requests.get(url).json()

def update(flight_source):
    response = get_data()

    # Convert to Pandas dataframe
    col_name = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'long', 'lat', 'baro_altitude', 'on_ground', 'velocity',
                'true_track', 'vertical_rate', 'sensors', 'geo_altitude', 'squawk', 'spi', 'position_source']
    flight_data = response['states']
    flight_df = pd.DataFrame(flight_data, columns=col_name)
    wgs84_to_web_mercator(flight_df)
    flight_df = flight_df.fillna('No Data')
    flight_df['rot_angle'] = -1 * flight_df['true_track']
    flight_df['url'] = ICON_URL
    
    # Convert to Bokeh datasource / streaming
    n_roll = len(flight_df.index)
    flight_source.stream(flight_df.to_dict(orient='list'), n_roll)


def plot(flight_source, x_range, y_range):
    p = figure(x_range=x_range, y_range=y_range, x_axis_type='mercator',
               y_axis_type='mercator', sizing_mode='scale_width', plot_height=300)
    tile_prov = get_provider(ESRI_IMAGERY)
    p.add_tile(tile_prov, level='image')
    p.image_url(url='url', x='x', y='y', source=flight_source, anchor='center',
                angle_units='deg', angle='rot_angle', h_units='screen', w_units='screen', w=40, h=40)
    p.circle('x', 'y', source=flight_source, fill_color='red',
             hover_color='yellow', size=10, fill_alpha=0.8, line_width=0)

    hover_tool = HoverTool()
    hover_tool.tooltips = [('Call sign', '@callsign'), ('Origin Country', '@origin_country'),
                           ('velocity(m/s)', '@velocity'), ('Altitude(m)', '@baro_altitude')]
    labels = LabelSet(x='x', y='y', text='callsign', level='glyph',
                      x_offset=5, y_offset=5, source=flight_source, render_mode='canvas', background_fill_color='white', text_font_size="8pt")
    p.add_tools(hover_tool)
    p.add_layout(labels)
    return p


def flight_tracking(doc):
    xy_min = wgs84_web_mercator_point(LON_MIN, LAT_MIN)
    xy_max = wgs84_web_mercator_point(LON_MAX, LAT_MAX)

    # Coordinate range in web mercator
    x_range, y_range = ([xy_min[0], xy_max[0]], [xy_min[1], xy_max[1]])

    # Init bokeh
    flight_source = ColumnDataSource({
        'icao24': [],
        'callsign': [],
        'origin_country': [],
        'time_position': [],
        'last_contact': [],
        'long': [],
        'lat': [],
        'baro_altitude': [],
        'on_ground': [],
        'velocity': [],
        'true_track': [],
        'vertical_rate': [],
        'sensors': [],
        'geo_altitude': [],
        'squawk': [],
        'spi': [],
        'position_source': [],
        'x': [],
        'y': [],
        'rot_angle': [],
        'url': []
    })

    # Update every 10 sec (unregistered user)
    doc.add_periodic_callback(
        partial(update, flight_source=flight_source),
        10000
    )
    p = plot(flight_source, x_range, y_range)
    doc.title = 'Near Real Time Flight Tracking'
    doc.add_root(p)