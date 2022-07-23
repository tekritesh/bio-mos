import streamlit as st
import pandas as pd
from datetime import datetime, date
from scipy.spatial.distance import cdist
import os
from google.cloud import bigquery
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium

def get_row_for_click(lat, lon, df):
    loc_of_interest = (lat, lon)
    coordinates = list(zip(df['latitude'], df['longitude']))
    index_of_min_distance = int(cdist([loc_of_interest], coordinates).argmin())
    return index_of_min_distance

st.set_page_config(layout="wide")

st.title("Occurence Data")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'molten-kit-354506-5d1350a7c9b8.json'
bigquery_client = bigquery.Client()

# Write Query on BQ
df = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
df = df.rename(columns={'decimalLatitude': 'latitude', 'decimalLongitude': 'longitude'})

start = st.sidebar.date_input("Start Date", date(2022, 1, 1))
end = st.sidebar.date_input("End Date", date(2022, 7, 1))

start_date = start.strftime("%Y-%m-%d")
end_date = end.strftime("%Y-%m-%d")

options = st.multiselect(
     'Select Species',
     df.species.unique(),
     [df.species.unique()[0], df.species.unique()[1]])

# select the species input
df = df[df['species'].isin(options)]

# subset by datetime user input
df['eventDate'] = pd.to_datetime(df['eventDate'])
df['eventDateFormatted'] = df['eventDate'].dt.date
df = df[(df['eventDateFormatted'] > start) & (df['eventDateFormatted'] < end)]

Map = leafmap.Map()
Map.add_basemap()
zoom = st.sidebar.number_input("Zoom", 0, 20, 11)
Map.set_center(-43.374, -22.916, zoom)
Map.add_points_from_xy(df, popup=["species"], x='longitude', y='latitude', layer_name="Occurence Data")

map_data = st_folium(Map, key="fig1", height=700, width=1000)

if map_data["last_object_clicked"]:
     index = get_row_for_click(map_data["last_object_clicked"]['lat'],
                       map_data["last_object_clicked"]['lng'],
                       df)
     with st.expander("Species Information"):
          col1, col2, col3 = st.columns(3)
          col1.metric("Kingdom", df.iloc[index]['kingdom'], help="Kingdom of the species")
          col2.metric("Class", df.iloc[index]['class'], help="Class of the species")
          col3.metric("Genus", df.iloc[index]['genus'], help="Genus type")

     with st.expander("Human Inteference Information"):
          col1, col2 = st.columns(2)
          col1.metric("Avg Radiance", "8.1", help="Light Pollution")
          col2.metric("Degree of Urbanization", "1.2", help="Urbanization info")

     with st.expander("Weather Covariates Information"):
          col1, col2 = st.columns(2)
          col1.metric("Temperature", "32.5", help="Temperature in C")
          col2.metric("wind speed", "1.2", help="Wind Speed in m/s")

     with st.expander("Covariate Information - Geographic"):
          col1, col2 = st.columns(2)
          col1.metric("Land Cover Type", "Built", help="Land Cover info")
          col2.metric("Soil ph", "6.5", help="Soil Info")

     with st.expander("Geographic Information"):
          df = df.astype(str)
          st.dataframe(df.iloc[index][['countryCode', 'stateProvince', 'latitude', 'longitude']].to_frame())

     with st.expander("Event Datetime Information"):
          df = df.astype(str)
          st.dataframe(df.iloc[index][['eventDate', 'day', 'month', 'year',
                                  'dateIdentified',
                                  'lastInterpreted',
                                  ]].to_frame())

     with st.expander("Observation Record Information"):
          df = df.astype(str)
          st.dataframe(df.iloc[index][['occurrenceID', 'basisOfRecord', 'collectionCode', 'year',
                                  'identifiedBy',
                                  'rightsHolder', 'recordedBy'
                                  ]].to_frame())

     with st.expander("Raw Data Download"):
          df = df.astype(str)
          st.dataframe(df)
          csv = df.to_csv().encode('utf-8')
          st.download_button(
               "Press to Download",
               csv,
               "file.csv",
               "text/csv",
               key='download-csv'
          )

