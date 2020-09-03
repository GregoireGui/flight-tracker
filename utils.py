import numpy as np

def wgs84_web_mercator_point(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360)) * k
    return (x, y)

def wgs84_to_web_mercator(df, lon='long', lat='lat'):
    x, y = wgs84_web_mercator_point(df[lon], df[lat])
    df['x'] = x
    df['y'] = y
    return df