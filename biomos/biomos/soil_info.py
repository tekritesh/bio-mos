"""Module that enlists functions to query soil information
"""

from owslib.wcs import WebCoverageService
from pyproj import Proj, transform
from PIL import Image
import numpy as np
from math import cos, pi
import pandas as pd
import logging

class SoilInfo():


    def __init__(self, log_level = logging.INFO):
        self.log = logging.getLogger("climate-logger")
        self.log.setLevel(log_level)
        self.soil_data_dict_with_conversion = {'phh2o': 10,
                                      'bdod': 100,
                                      'cec': 10,
                                      'cfvo': 10,
                                      'clay': 10,
                                      'nitrogen': 100,
                                      'sand': 10,
                                      'silt': 10,
                                      'soc': 10,
                                      'ocd': 10
                                      }
        self.wcs = self.__set_wcs()

    def __set_wcs(self):
        wcs = {}
        for datatype, conversion_factor in self.soil_data_dict_with_conversion.items():
            wcs[datatype] = WebCoverageService(f'http://maps.isric.org/mapserv?map=/map/{datatype}.map',
                                     version='2.0.1')
        return wcs

    def __get_projection_epsg(country):
        if country == 'BR':
            return 29101
        elif country == 'GB':
            return 27700
        elif country == "":
            return -1


    def __get_bounding_box(self, latitude, longitude, projection_epsg):
        r_earth = 6371000.0
        displacement = 1000
        latitude_max = latitude + (displacement / r_earth) * (180 / pi)
        longitude_max = longitude + (displacement / r_earth) * (180 / pi) / cos(latitude * pi / 180)

        latitude_min = latitude - (displacement / r_earth) * (180 / pi)
        longitude_min = longitude - (displacement / r_earth) * (180 / pi) / cos(latitude * pi / 180)

        projection = Proj(init=f'epsg:{projection_epsg}')
        geographic = Proj(init='epsg:4326')

        x_cord_max, y_cord_max = transform(geographic, projection, longitude_max, latitude_max)

        x_cord_min, y_cord_min = transform(geographic, projection, longitude_min, latitude_min)

        subsets = [('X', x_cord_min, x_cord_max), ('Y', y_cord_min, y_cord_max)]

        return subsets

    def __get_soil_data(self, wcs, subsets, projection_epsg):
        soil_covariates = {}
        for datatype, conversion_factor in self.soil_data_dict_with_conversion.items():
            cov_id = f'{datatype}_0-5cm_mean'
            crs = f"http://www.opengis.net/def/crs/EPSG/0/{projection_epsg}"

            response = wcs[datatype].getCoverage(
                identifier=[cov_id],
                crs=crs,
                subsets=subsets,
                format='GEOTIFF_INT16')

            with open('test.tif', 'wb') as file:
                file.write(response.read())

            im = Image.open('test.tif')

            imarray = np.array(im)
            median_value = np.median(imarray) / conversion_factor

            soil_covariates[datatype] = median_value
        return soil_covariates

    def get_soil_info(self,lat_deg, lon_deg, country_code=''):
        """Function to Get Soil Composition Information for a given lat,lon and country code.
            lat_deg(float): latitude coordinates in degrees
            lon_deg(float): longitude coordinates in degrees
            country_code (str): 2 digit ISO country code
        """
        
        projection_epsg = self.__get_projection_epsg(country = country_code)
        subsets = self.__get_bounding_box(lat_deg, lon_deg, projection_epsg)
        soil_covariates = self.__get_soil_data( self.wcs, subsets, projection_epsg)
        soil_covariates['decimalLatitude'] = lat_deg
        soil_covariates['decimalLongitude'] = lon_deg

        
        return soil_covariates