"""Module that enlists functions to query land cover labels
"""

import ee
import geemap
from datetime import timedelta, datetime
import pandas as pd
from math import pi, cos
import logging


class LandCoverLabel():

    def __init__(self, log_level = logging.INFO):
        self.log = logging.getLogger("climate-logger")
        self.log.setLevel(log_level)
        # service_account = '292293468099-compute@developer.gserviceaccount.com'
        # credentials = ee.ServiceAccountCredentials(service_account, '/mnt/.cred/gbif-challenge-a41b66fe5446.json')
        try:
            ee.Initialize()
        except Exception as e:
            ee.Authenticate()
            ee.Initialize()

    # def get_gbif_data(self):
    #     brazil_data = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
    #     uk_data = pd.read_csv('bquxjob_39d5dfa3_181e432946c.csv')

    #     all_data = pd.concat([brazil_data, uk_data])
    #     all_data = all_data.reset_index(drop=True)
    #     return all_data

    def __create_bounding_box(self, lat, lon):
        r_earth = 6371000.0
        displacement = 1000
        latitude_max = lat + (displacement / r_earth) * (180 / pi)
        longitude_max = lon + (displacement / r_earth) * (180 / pi) / cos(lat * pi / 180)

        latitude_min = lat - (displacement / r_earth) * (180 / pi)
        longitude_min = lon - (displacement / r_earth) * (180 / pi) / cos(lat * pi / 180)
        region = ee.Geometry.BBox(longitude_min, latitude_min, longitude_max, latitude_max)

        return region

    def get_land_cover_data(self,lat_deg, lon_deg,event_date):
        """Function to Get Land Cover Label from Geemap for a given longitude and latitude and date
            lat_deg(float): latitude coordinates in degrees
            lon_deg(float): longitude coordinates in degrees
            event_date (str): Date in '%Y-%m-%dT%H:%M:%S%z' format
        """



        land_cover_label = []
        try:
    
            # lat = row['decimalLatitude']
            # lon = row['decimalLongitude']
            region = self.__create_bounding_box(lat_deg, lon_deg)
            end_date = datetime.strptime(event_date, '%Y-%m-%dT%H:%M:%S%z')
            start_date = end_date - timedelta(days=365)
            end_date = end_date.strftime('%Y-%m-%d')
            start_date = start_date.strftime('%Y-%m-%d')
            dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate(start_date, end_date).filterBounds(region).mode()
            dwImage = dw.clip(region)
            label_index = round(dwImage.reduceRegion(reducer=ee.Reducer.mode(), scale=100).get('label').getInfo())
            label_type = dwImage.getInfo()['bands'][label_index]['id']
            land_cover_label.append(label_type)
        except Exception:
            print('problem')
            # problematic_data.append(row)
            # land_cover_label.append(None)
        
        return land_cover_label