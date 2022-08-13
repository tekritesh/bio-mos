"""Module that enlists functions to query soil information
"""

from owslib.wcs import WebCoverageService
from pyproj import Proj, transform
from PIL import Image
import numpy as np
from math import cos, pi
import pandas as pd
import logging
import ee

class SoilComposition():

    def __init__(self, log_level = logging.INFO):
        self.log = logging.getLogger("climate-logger")
        self.log.setLevel(log_level)

        try:
            ee.Initialize()
        except Exception as e:
            ee.Authenticate()
            ee.Initialize()

    def __get_bounding_box(self, lat_deg, lon_deg):
        r_earth = 6371000.0
        displacement = 1000
        lat_deg_max = lat_deg + (displacement / r_earth) * (180 / pi)
        lon_deg_max = lon_deg + (displacement / r_earth) * (180 / pi) / cos(lat_deg * pi / 180)
        lat_deg_min = lat_deg - (displacement / r_earth) * (180 / pi)
        lon_deg_min = lon_deg - (displacement / r_earth) * (180 / pi) / cos(lat_deg * pi / 180)

        roi = ee.Geometry.BBox(lon_deg_min, lat_deg_min, lon_deg_max, lat_deg_max)
        return roi

    def get_soil_data(self, lat_deg, lon_deg):
        
        """Function to Get Soil Compostion from Geemap for a given longitude and latitude
            lat_deg(float): latitude coordinates in degrees
            lon_deg(float): longitude coordinates in degrees
        """

        try:
            roi = self.__get_bounding_box(lat_deg,lon_deg)
            SGc = ee.Image("projects/soilgrids-isric/clay_mean").clip(roi)   # clay
            SGs = ee.Image("projects/soilgrids-isric/sand_mean").clip(roi)  # sand
            SGbd = ee.Image("projects/soilgrids-isric/bdod_mean").clip(roi)  # bulk density
            SGsoc = ee.Image("projects/soilgrids-isric/soc_mean").clip(roi)  # SOC
            SGpH = ee.Image("projects/soilgrids-isric/phh2o_mean").clip(roi) # pH H2O
            SGcec = ee.Image("projects/soilgrids-isric/cec_mean").clip(roi)  # CEC
            SGcf = ee.Image("projects/soilgrids-isric/cfvo_mean").clip(roi)  # coarse fragments
            SGn = ee.Image("projects/soilgrids-isric/nitrogen_mean").clip(roi) # nitrogen
            SGsi = ee.Image("projects/soilgrids-isric/silt_mean").clip(roi)  # silt
            SGocd = ee.Image("projects/soilgrids-isric/ocd_mean").clip(roi)  # ocd

            SG = SGc.addBands(SGs).addBands(SGbd).addBands(SGsoc).addBands(SGpH).\
                addBands(SGcec).addBands(SGcf).addBands(SGn).addBands(SGsi).addBands(SGocd)

            SG = SG.select('phh2o_0-5cm_mean','bdod_0-5cm_mean','cec_0-5cm_mean','cfvo_0-5cm_mean', 'clay_0-5cm_mean',
        'nitrogen_0-5cm_mean','sand_0-5cm_mean','silt_0-5cm_mean', 'soc_0-5cm_mean','ocd_0-5cm_mean')

            SGmean = SG.reduceRegion(ee.Reducer.median(),
                geometry = roi)
            data_dict = SGmean.getInfo()
            data = pd.DataFrame([data_dict], columns=data_dict.keys())

        except:
            column_names = ['phh2o_0-5cm_mean','bdod_0-5cm_mean','cec_0-5cm_mean','cfvo_0-5cm_mean', 'clay_0-5cm_mean',
                            'nitrogen_0-5cm_mean','sand_0-5cm_mean','silt_0-5cm_mean','soc_0-5cm_mean','ocd_0-5cm_mean']
            data = pd.DataFrame([[np.nan]*len(column_names)],columns = column_names)

        return data