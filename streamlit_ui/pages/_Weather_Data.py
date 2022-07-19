import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import os
from google.cloud import bigquery

st.set_page_config(layout="wide",
                   page_title="Weather Data",
                   page_icon="🔥"
                   )

st.title("Temperature Data using DeckGL")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'molten-kit-354506-5d1350a7c9b8.json'
bigquery_client = bigquery.Client()

# Write Query on BQ
QUERY = """
SELECT  * FROM `molten-kit-354506.sample_gbif_climate.climate_bulk_download_BZ_2022`
  """

Query_Results = bigquery_client.query(QUERY)
df = Query_Results.to_dataframe()


st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/dark-v9',
     initial_view_state=pdk.ViewState(
         latitude=-2.00,
         longitude=-54.08,
         zoom=5,
         pitch=50,
     ),
     layers=[
         pdk.Layer(
            'HeatmapLayer',
            data=df,
            opacity=0.9,
            get_position='[lon, lat]',
            get_weight='t2m',
            pickable=True,
            auto_highlight=True
         ),
     ],
 ))
