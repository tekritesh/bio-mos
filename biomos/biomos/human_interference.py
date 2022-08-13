"""Module to pull data for light pollution and human settlement data.
"""

import pandas as pd
import ee
import numpy as np

class HumanInterference():
    """Class to initiliaze google earth engine
    Provides functions to get average radiance given lat_deg lon_deg
    and human settlement information
    """
    def __init__(self):
        try:
            ee.Initialize()
        except Exception as e:
            ee.Authenticate()
            ee.Initialize()
        self.ghsl = ee.ImageCollection('JRC/GHSL/P2016/SMOD_POP_GLOBE_V1').\
                        filter(ee.Filter.date('2015-01-01', '2015-12-31')).select('smod_code').median()


    def get_avg_radiance(self, lat_deg, lon_deg, event_date, buffer=20000, scale=100):
        """
        lat_deg: latitude coordinates
        lon_deg: longitude coordinates
        event_date: date of gbif occurrence
        scale: pixel scale value
        buffer (int): value in meters of radius around center lat_deg lon_deg
        """
        yy = event_date.split('-')[0] 
        mm = event_date.split('-')[1] 
        start = yy + '-' + mm + '-01' ##get data for the month
        
        viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG").\
                        filterDate(start).select('avg_rad').median()

        aoi = ee.Geometry.Point([lon_deg, lat_deg]).buffer(buffer)
        viirs_clipped = viirs.clip(aoi)
        
        avg_rad = viirs_clipped.reduceRegion(reducer=ee.Reducer.mean(),
                                        geometry = None,
                                        scale=scale,
                                        maxPixels=1e9).get('avg_rad')
        
        return avg_rad.getInfo()

    def get_avg_deg_urban(self, lat_deg, lon_deg, buffer=10000, scale=100):
        """
        lat_deg: laitude coordinates
        lon_deg: longitude coordinates
        scale: pixel scale value
        buffer (int): value in meters of radius around center lat_deg lon_deg
        """
        aoi = ee.Geometry.Point([lon_deg, lat_deg]).buffer(buffer)
        ghsl_clipped = self.ghsl.clip(aoi)
        
        smod_code = ghsl_clipped.reduceRegion(reducer=ee.Reducer.mean(),
                                        geometry = None,
                                        scale=scale,
                                        maxPixels=1e9).get('smod_code')
        
        return smod_code.getInfo()