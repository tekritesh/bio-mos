import pandas as pd
import datetime
import ee
import streamlit as st
import geemap.foliumap as geemap
#import geemap

st.set_page_config(layout="wide",
                   page_title="Land Cover",
                   page_icon="🌎")

st.title("Land Cover Map")

df = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
df = df.rename(columns={'decimalLatitude': 'latitude', 'decimalLongitude': 'longitude'})

Map = geemap.Map()
Map.add_basemap("HYBRID")

longitude = st.sidebar.number_input("Longitude", -180.0, 180.0, -43.374)
latitude = st.sidebar.number_input("Latitude", -90.0, 90.0, -22.916)
zoom = st.sidebar.number_input("Zoom", 0, 20, 11)

Map.setCenter(longitude, latitude, zoom)

start = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end = st.sidebar.date_input("End Date", datetime.date(2022, 7, 1))

start_date = start.strftime("%Y-%m-%d")
end_date = end.strftime("%Y-%m-%d")

# subset by datetime user input
df['eventDate'] = pd.to_datetime(df['eventDate'])
df['eventDateFormatted'] = df['eventDate'].dt.date
df = df[(df['eventDateFormatted'] > start) & (df['eventDateFormatted'] < end)]

region = ee.Geometry.BBox(-179, -89, 179, 89)
dw = geemap.dynamic_world(region, start_date, end_date, return_type="hillshade")

layers = {
    "Dynamic World": geemap.ee_tile_layer(dw, {}, "Dynamic World Land Cover"),
}
Map.addLayer(dw, {}, 'Dynamic World Land Cover cover')
Map.add_legend(
    title="Dynamic World Land Cover",
    builtin_legend="Dynamic_World",
)
df.to_csv('test.csv')
Map.add_points_from_xy(df, popup=["species"], x='longitude', y='latitude', layer_name="Occurence Data")

Map.to_streamlit(height=750)
