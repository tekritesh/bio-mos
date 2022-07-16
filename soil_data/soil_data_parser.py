from owslib.wcs import WebCoverageService
from pyproj import Proj, transform
from PIL import Image
import numpy as np
from math import cos, pi
import pandas as pd


class SoilDataParser:

    soil_data_dict_with_conversion = {'phh2o': 10,
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

    def set_wcs(self):
        wcs = {}
        for datatype, conversion_factor in self.soil_data_dict_with_conversion.items():
            wcs[datatype] = WebCoverageService(f'http://maps.isric.org/mapserv?map=/map/{datatype}.map',
                                     version='2.0.1')
        return wcs

    @staticmethod
    def get_projection_epsg(country):
        if country == 'BR':
            return 29101
        elif country == 'GB':
            return 27700

    def get_gbif_data(self):
        brazil_data = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
        uk_data = pd.read_csv('bquxjob_39d5dfa3_181e432946c.csv')

        gbif_data = pd.concat([brazil_data, uk_data])
        gbif_data = gbif_data.reset_index(drop=True)

        return gbif_data

    def get_bounding_box(self, latitude, longitude, projection_epsg):
        r_earth = 6371000.0
        displacement = 250
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

    def get_soil_data(self, wcs, subsets, projection_epsg):
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

    def get_soil_covaraites_for_gbif_data(self):
        gbif_data = self.get_gbif_data()
        wcs = self.set_wcs()
        all_data_list = []

        for index, row in gbif_data.iterrows():
            latitude = row['decimalLatitude']
            longitude = row['decimalLongitude']
            projection_epsg = self.get_projection_epsg(row['countryCode'])
            subsets = self.get_bounding_box(latitude, longitude, projection_epsg)
            soil_covariates = self.get_soil_data(wcs, subsets, projection_epsg)

            soil_covariates['decimalLatitude'] = latitude
            soil_covariates['decimalLongitude'] = longitude
            soil_covariates['eventDate'] = row['eventDate']
            all_data_list.append(pd.DataFrame(soil_covariates, index=[index]))
        return all_data_list


all_data_list = SoilDataParser().get_soil_covaraites_for_gbif_data()
all_data = pd.concat[all_data_list]
all_data.to_csv('soil_data.csv')




