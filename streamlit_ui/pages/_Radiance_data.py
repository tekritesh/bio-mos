import streamlit as st
import leafmap.foliumap as leafmap
import os
from google.cloud import bigquery

st.set_page_config(layout="wide",
                   page_title="Radiance Data",
                   page_icon="💡"
                   )

st.title("Radiance Data")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'molten-kit-354506-5d1350a7c9b8.json'
bigquery_client = bigquery.Client()

# Write Query on BQ
QUERY = """
SELECT  * FROM `molten-kit-354506.sample_gbif_human_interference.gbif_human_BR_2022` LIMIT 1000
  """

Query_Results = bigquery_client.query(QUERY)
df = Query_Results.to_dataframe()

m = leafmap.Map(tiles="stamentoner")
m.add_heatmap(
    df,
    latitude="decimalLatitude",
    longitude="decimalLongitude",
    value="avg_radiance",
    name="Heat map",
    radius=20,
)
m.to_streamlit(width=700, height=500)