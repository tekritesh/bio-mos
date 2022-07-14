"""Module that enlists all the functions that need to be called in the airflow orchestration pipeline
to append covariates to the gbif occurrence data.
"""
import pandas as pd
import numpy as np
import ee
from pygbif import occurrences as occ

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
        
        return avg_rad.getInfo()

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
        
        return smod_code.getInfo()

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

        return self.df[['decimalLatitude', 'decimalLongitude', 
        'countryCode', 'eventDate',  'avg_radiance', 'avg_deg_urban', 'scientificName']].copy()
            
