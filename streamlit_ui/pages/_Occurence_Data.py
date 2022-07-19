import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from google.cloud import bigquery

st.set_page_config(layout="wide")

st.title("Occurence Data")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'molten-kit-354506-5d1350a7c9b8.json'
bigquery_client = bigquery.Client()

# Write Query on BQ
df = pd.read_csv('bquxjob_2c525673_181e4342f32.csv')
df = df.rename(columns={'decimalLatitude': 'lat', 'decimalLongitude': 'lon'})

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

st.map(df)