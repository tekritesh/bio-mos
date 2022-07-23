import datetime
import pandas as pd
import ee
import streamlit as st
import geemap.foliumap as geemap
import geemap.colormaps as cm


st.set_page_config(layout="wide",
                   page_title="Soil Data",
                   page_icon="🌎")

st.title("Soil Data")

Map = geemap.Map()
#Map.add_basemap("HYBRID")

df = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
df = df.rename(columns={'decimalLatitude': 'latitude', 'decimalLongitude': 'longitude'})

longitude = st.sidebar.number_input("Longitude", -180.0, 180.0, -43.374)
latitude = st.sidebar.number_input("Latitude", -90.0, 90.0, -22.916)
zoom = st.sidebar.number_input("Zoom", 0, 20, 11)

Map.setCenter(longitude, latitude, zoom)

start = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end = st.sidebar.date_input("End Date", datetime.date(2022, 7, 1))
option = st.selectbox(
     'Select Soil Layer',
     ('Bulk Density (cg/cm³)', 'Cation Exchange Capacity (mmol(c)/kg)',
      'Coarse fragment (cm3/dm3)', 'Clay (g/kg)', 'Nitrogen (cg/kg)', 'pH Level (ph*10)',
      'Sand (g/kg)', 'Silt (g/kg)', 'Soil Organic Content (dg/kg)',
      'Organic carbon density (hg/m³)'))

soil_meta = {'Bulk Density (cg/cm³)': {'layer': 'bdod_0-5cm_mean', 'min': 60, 'max': 175, 'ee_name': 'bdod_mean'},
             'Cation Exchange Capacity (mmol(c)/kg)': {'layer': 'cec_0-5cm_mean', 'min': 0, 'max': 300, 'ee_name': 'cec_mean'},
             'Coarse fragment (cm3/dm3)': {'layer': 'cfvo_0-5cm_mean', 'min': 0, 'max': 250, 'ee_name': 'cfvo_mean'},
             'Clay (g/kg)': {'layer': 'clay_0-5cm_mean', 'min': 0, 'max': 800, 'ee_name': 'clay_mean'},
             'Silt (g/kg)': {'layer': 'silt_0-5cm_mean', 'min': 0, 'max': 800, 'ee_name': 'silt_mean'},
             'Soil Organic Content (dg/kg)': {'layer': 'soc_0-5cm_mean', 'min': 0, 'max': 4200, 'ee_name': 'soc_mean'},
             'Organic carbon density (hg/m³)': {'layer': 'ocd_0-5cm_mean', 'min': 0, 'max': 1224, 'ee_name': 'ocd_mean'},
             'pH Level (ph*10)': {'layer': 'phh2o_0-5cm_mean', 'min': 0, 'max': 140, 'ee_name': 'phh2o_mean'},
             'Sand (g/kg)': {'layer': 'sand_0-5cm_mean', 'min': 0, 'max': 800, 'ee_name': 'sand_mean'},
             'Nitrogen (cg/kg)': {'layer': 'nitrogen_0-5cm_mean', 'min': 0, 'max': 1240, 'ee_name': 'nitrogen_mean'}
             }

start_date = start.strftime("%Y-%m-%d")
end_date = end.strftime("%Y-%m-%d")

# subset by datetime user input
df['eventDate'] = pd.to_datetime(df['eventDate'])
df['eventDateFormatted'] = df['eventDate'].dt.date
df = df[(df['eventDateFormatted'] > start) & (df['eventDateFormatted'] < end)]

region = ee.Geometry.BBox(-179, -89, 179, 89)
dw = ee.Image(f"projects/soilgrids-isric/{soil_meta[option]['ee_name']}")
palette = cm.palettes.coolwarm.default
imageVisParam = {"bands": [soil_meta[option]['layer']], 'min': soil_meta[option]['min'],
                 'max': soil_meta[option]['max'], "opacity": 0.8,
                 "palette": list(palette)}

Map.addLayer(dw, imageVisParam, option)
Map.add_colorbar(imageVisParam, label=option)
Map.add_points_from_xy(df, popup=["species"], x='longitude', y='latitude', layer_name="Occurence Data")
Map.to_streamlit(height=750)
