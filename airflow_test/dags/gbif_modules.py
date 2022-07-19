"""Module that enlists all the functions that need to be called in the airflow orchestration pipeline
to append covariates to the gbif occurrence data.
"""
import pandas as pd
import numpy as np
import ee
from pygbif import occurrences as occ
from meteostat import Point, Daily
from datetime import timedelta, datetime

from math import cos, pi


def get_occurrences(eventDate, country, offset = 0):
    """function to get the occurrences from gbif. max rows in one call is 300; we use a loop
    args:
        eventDate (str): day to get the data for
        country (str): 2 digit ISO country code
        offset (int): offset parameter to loop through occurrences in gbif
    """
    cols_list = ['key','datasetKey','publishingCountry', 'protocol','lastCrawled','lastParsed',
                 'crawlId','basisOfRecord','occurrenceStatus','taxonKey','kingdomKey','phylumKey',
                 'classKey','orderKey','familyKey', 'genusKey','speciesKey','acceptedTaxonKey',
                 'scientificName','acceptedScientificName', 'kingdom', 'phylum', 'order','family',
                 'genus', 'species', 'genericName','specificEpithet', 'taxonRank', 'taxonomicStatus',
                 'iucnRedListCategory','decimalLongitude', 'decimalLatitude', 'coordinateUncertaintyInMeters',
                 'year','month', 'day', 'eventDate', 'issues','modified', 'lastInterpreted', 'recordedBy',
                 'identifiedBy', 'class', 'countryCode', 'country', 'dateIdentified', 'datasetName']
    batch_size = 300 #max rows outputted by pygbif client
    output_rows = batch_size
    out_df = pd.DataFrame()
    while output_rows >= batch_size:
        temp_df = pd.DataFrame(occ.search(eventDate=eventDate, country=country,
                                          offset=offset, hasCoordinate=True)['results'])
        offset += batch_size
        output_rows = temp_df.shape[0]
        out_df = pd.concat([out_df,temp_df])
    #out_df[cols_list].to_csv("test_data.csv", index=False)
    return out_df[cols_list]

class HumanInterference():
    """Class to initiliaze google earth engine
    Provides functions to get average radiance given lat lon
    and human settlement information
    """
    def __init__(self, df):
        try:
            ee.Initialize()
        except Exception as e:
            ee.Authenticate()
            ee.Initialize()
        self.ghsl = ee.ImageCollection('JRC/GHSL/P2016/SMOD_POP_GLOBE_V1').\
                        filter(ee.Filter.date('2015-01-01', '2015-12-31')).select('smod_code').median()
        self.df = df


    def get_avg_radiance(self, lat, lon, date, buffer=20000, scale=100):
        """
        lat: latitude coordinates
        lon: longitude coordinates
        date: date of gbif occurrence
        scale: pixel scale value
        buffer (int): value in meters of radius around center lat lon
        """
        try: 
            ## data only available till 2022/05/01 (updated quarterly)
            yy = date.split('-')[0] 
            mm = date.split('-')[1] 
            start = yy + '-' + mm + '-01' ##get data for the month
            
            viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG").\
                            filterDate(start).select('avg_rad').median()

            aoi = ee.Geometry.Point([lon, lat]).buffer(buffer)
            viirs_clipped = viirs.clip(aoi)
            
            avg_rad = viirs_clipped.reduceRegion(reducer=ee.Reducer.mean(),
                                            geometry = None,
                                            scale=scale,
                                            maxPixels=1e9).get('avg_rad')
            
            return round(avg_rad.getInfo(),4)
        except:
            return np.nan


    def get_avg_deg_urban(self, lat, lon, buffer=10000, scale=100):
        """
        lat: latitude coordinates
        lon: longitude coordinates
        scale: pixel scale value
        buffer (int): value in meters of radius around center lat lon
        """
        aoi = ee.Geometry.Point([lon, lat]).buffer(buffer)
        ghsl_clipped = self.ghsl.clip(aoi)
        
        smod_code = ghsl_clipped.reduceRegion(reducer=ee.Reducer.mean(),
                                        geometry = None,
                                        scale=scale,
                                        maxPixels=1e9).get('smod_code')
        
        return round(smod_code.getInfo(), 4)

    def human_wrapper(self):
        self.df['date'] = self.df['eventDate'].astype(str).str[:10]
        self.df['avg_radiance'] = self.df[['decimalLatitude',
                                        'decimalLongitude',
                                        'date']].\
                                        apply(lambda x: self.get_avg_radiance(x.decimalLatitude,
                                                                            x.decimalLongitude,
                                                                        x.date),
                                            axis=1)

        self.df['avg_deg_urban'] = self.df[['decimalLatitude',
                                        'decimalLongitude']].\
                                        apply(lambda x: self.get_avg_deg_urban(x['decimalLatitude'],
                                                                            x['decimalLongitude']),
                                            axis=1)

        return self.df[['key','decimalLatitude', 'decimalLongitude', 
        'countryCode', 'eventDate',  'avg_radiance', 'avg_deg_urban', 'scientificName']].copy()
            

class GetClimateData():
    """Class to invoke meteo stat apis to get daily data 
    """
    def __init__(self, df):
        self.df = df
        # utils.logger.setLevel(log_level)

    def get_interpolated_climate_data(self,lat_deg, lon_deg,start_date, end_date, altitude=0 ):
        """Function to Get Interpolated climate data for lat,lon,altitude for a given date
        Refer : https://dev.meteostat.net/python/point.html#api for a complete picture

        lat_deg(float): latitude coordinates in degrees
        lon_deg(float): longitude coordinates in degrees
        altitude(float): altitude of the geo co-ordinate in meters
        start_date(string): start date for climate data
        end_date(string): end date for climate data
        """
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        location = Point(lat_deg, lon_deg, altitude)

        #utils.logger.info("Getting climate data for Lat,Log:[%f,%f] for dates:[%s, %s]" % (lat_deg, lon_deg, start_date, end_date))
        column_names = ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun' ]
        try:
            data = Daily(location, start_date, end_date)
            data = data.fetch().reset_index()
            if data.shape[0] < 1:
                data = pd.DataFrame([[np.nan]*len(column_names)],columns = column_names)
            #utils.logger.info("Recieved Data Points: %d" %(len(data.index)))
        except Exception as e:
            #utils.logger.error(e)
            data = pd.DataFrame([[np.nan]*len(column_names)],columns = column_names)
            
        return data.loc[0,'tavg'], data.loc[0,'tmin'], data.loc[0,'tmax'], data.loc[0,'prcp'], \
                data.loc[0,'snow'], data.loc[0,'wdir'], data.loc[0,'wspd'], data.loc[0,'wpgt'],\
                     data.loc[0,'pres'], data.loc[0,'tsun']

    def climate_wrapper(self):
        self.df['date'] = self.df['eventDate'].astype(str).str[:10]
        self.df[['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun' 
        ]] = self.df[['decimalLatitude',
                                        'decimalLongitude',
                                        'date']].\
                                        apply(lambda x: self.get_interpolated_climate_data(lat_deg= x.decimalLatitude,
                                                                            lon_deg=x.decimalLongitude,
                                                                        start_date= x.date,
                                                                        end_date= x.date),
                                            axis=1, result_type="expand")
        

        return self.df[['key','decimalLatitude', 'decimalLongitude', 'countryCode', 'eventDate', 
        'tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']].copy()



class SoilData():

    def __init__(self, df):
        try:
            ee.Initialize()
        except Exception as e:
            ee.Authenticate()
            ee.Initialize()
        self.df = df

    def get_bounding_box(self, latitude, longitude):
        r_earth = 6371000.0
        displacement = 1000
        latitude_max = latitude + (displacement / r_earth) * (180 / pi)
        longitude_max = longitude + (displacement / r_earth) * (180 / pi) / cos(latitude * pi / 180)
        latitude_min = latitude - (displacement / r_earth) * (180 / pi)
        longitude_min = longitude - (displacement / r_earth) * (180 / pi) / cos(latitude * pi / 180)

        roi = ee.Geometry.BBox(longitude_min, latitude_min, longitude_max, latitude_max)
        return roi

    def get_soil_data(self, latitude, longitude):

        try:
            roi = self.get_bounding_box(latitude,longitude)
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

        return data.loc[0,'phh2o_0-5cm_mean'], data.loc[0,'bdod_0-5cm_mean'], data.loc[0,'cec_0-5cm_mean'],\
                 data.loc[0,'cfvo_0-5cm_mean'], data.loc[0,'clay_0-5cm_mean'], data.loc[0,'nitrogen_0-5cm_mean'], data.loc[0,'sand_0-5cm_mean'], \
                 data.loc[0,'silt_0-5cm_mean'], data.loc[0,'soc_0-5cm_mean'], data.loc[0,'ocd_0-5cm_mean']


    def soil_wrapper(self):
        self.df[['phh2o_0_5cm_mean','bdod_0_5cm_mean','cec_0_5cm_mean','cfvo_0_5cm_mean', 'clay_0_5cm_mean',
        'nitrogen_0_5cm_mean','sand_0_5cm_mean','silt_0_5cm_mean',
        'soc_0_5cm_mean','ocd_0_5cm_mean']] = self.df[['decimalLatitude',
                                        'decimalLongitude']].\
                                        apply(lambda x: self.get_soil_data(x.decimalLatitude,
                                        x.decimalLongitude),
                                            axis=1, result_type="expand")

        return self.df[['key','decimalLatitude', 'decimalLongitude', 'countryCode', 'eventDate', 
        'phh2o_0_5cm_mean','bdod_0_5cm_mean','cec_0_5cm_mean', 'cfvo_0_5cm_mean', 'clay_0_5cm_mean',
        'nitrogen_0_5cm_mean','sand_0_5cm_mean','silt_0_5cm_mean','soc_0_5cm_mean','ocd_0_5cm_mean']].copy()


class LandCover():
    def __init__(self, df):
        try:
            ee.Initialize()
        except Exception as e:
            ee.Authenticate()
            ee.Initialize()
        self.df = df

    def create_bounding_box(self, lat, lon):
        r_earth = 6371000.0
        displacement = 1000
        latitude_max = lat + (displacement / r_earth) * (180 / pi)
        longitude_max = lon + (displacement / r_earth) * (180 / pi) / cos(lat * pi / 180)

        latitude_min = lat - (displacement / r_earth) * (180 / pi)
        longitude_min = lon - (displacement / r_earth) * (180 / pi) / cos(lat * pi / 180)
        region = ee.Geometry.BBox(longitude_min, latitude_min, longitude_max, latitude_max)

        return region

    
    def get_land_label(self, lat_deg, lon_deg, date):
        try:
            #utils.logger.info("Getting Land Label for [%f,%f] for [%s,%s]" %(lat_deg,lon_deg,start_date,end_date))
            region = self.create_bounding_box(lat_deg, lon_deg)
            end_date = datetime.fromisoformat(date)
            start_date = end_date - timedelta(days=365)
            end_date = end_date.strftime('%Y-%m-%d')
            start_date = start_date.strftime('%Y-%m-%d')
            dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate(start_date, end_date).filterBounds(region).mode()
            dwImage = dw.clip(region)
            label_index = round(dwImage.reduceRegion(reducer=ee.Reducer.mode(), scale=100).get('label').getInfo())
            label_type = dwImage.getInfo()['bands'][label_index]['id']
        except Exception as e:
            #utils.logger.error(e)
            label_type = ""
        return label_type

    def land_cover_wrapper(self):
        self.df['date'] = self.df['eventDate'].astype(str).str[:10]
        self.df['land_cover_label'] = self.df[['decimalLatitude',
                                        'decimalLongitude',
                                        'date']].\
                                        apply(lambda x: self.get_land_label(x.decimalLatitude,
                                                                            x.decimalLongitude,
                                                                        x.date),
                                            axis=1)


        return self.df[['key','decimalLatitude', 'decimalLongitude', 
        'countryCode', 'eventDate', 'land_cover_label']].copy()
