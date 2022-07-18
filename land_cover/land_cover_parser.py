import ee
import geemap
from datetime import timedelta, datetime
import pandas as pd
from math import pi, cos


class LandCoverParser():

    def get_gbif_data(self):
        brazil_data = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
        uk_data = pd.read_csv('bquxjob_39d5dfa3_181e432946c.csv')

        all_data = pd.concat([brazil_data, uk_data])
        all_data = all_data.reset_index(drop=True)
        return all_data

    def create_bounding_box(self, lat, lon):
        r_earth = 6371000.0
        displacement = 1000
        latitude_max = lat + (displacement / r_earth) * (180 / pi)
        longitude_max = lon + (displacement / r_earth) * (180 / pi) / cos(lat * pi / 180)

        latitude_min = lat - (displacement / r_earth) * (180 / pi)
        longitude_min = lon - (displacement / r_earth) * (180 / pi) / cos(lat * pi / 180)
        region = ee.Geometry.BBox(longitude_min, latitude_min, longitude_max, latitude_max)

        return region

    def get_land_cover_data(self, gbif_data):
        land_cover_label = []
        problematic_data = []
        for index, row in gbif_data.iterrows():
            try:
                ee.Initialize()
                lat = row['decimalLatitude']
                lon = row['decimalLongitude']
                region = self.create_bounding_box(lat, lon)
                end_date = datetime.strptime(row['eventDate'], '%Y-%m-%dT%H:%M:%S%z')
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
                problematic_data.append(row)
                land_cover_label.append(None)

        gbif_data['land_cover'] = land_cover_label
        return gbif_data[['decimalLatitude', 'decimalLongitude', 'eventDate', 'land_cover']]


if __name__ == "__main__":
    gbif_data = LandCoverParser().get_gbif_data()
    land_cover = LandCoverParser().get_land_cover_data(gbif_data)