import os 
import pandas as pd
import numpy as np
import datetime as dt
import time
# import ee
# import geemap as geemap
from io import BytesIO
from IPython.display import HTML

import panel as pn
import param
import plotly.express as px
import plotly.graph_objects as go


from meteostat import Point, Daily

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../gbif-challenge-953ed382a2dd.json" ##change this

from google.cloud import bigquery

client = bigquery.Client()


# df = pd.read_csv('human_interference_sample.csv')
df = pd.read_csv("/Users/riteshtekriwal/Work/Data/Raw/bio-conservation/test_combined.csv")

# df.head()

################################## All the filter widgets we need
start_date = pn.widgets.DatePicker(name='Start Date', start = dt.date(2021, 12, 1),
                                  end=dt.date(2022, 4, 30), value = dt.date(2022, 4, 4))

end_date = pn.widgets.DatePicker(name='End Date', start = dt.date(2021, 12, 1),
                                  end=dt.date(2022, 4, 30), value = dt.date(2022, 4, 6))

country = pn.widgets.Select(name='Country', options=list(df.country.unique()))
species = pn.widgets.Select(name='Species', options=list(df.species.unique()))

button = pn.widgets.Button(name='Update Plots', width= 200, button_type='primary')

##################################### All our plot functions

## the world map view of occurrence data
def occ_plot(df=df, species=''):
    # fig = px.scatter_geo(df, lat="decimalLatitude", lon='decimalLongitude', color='species')
    # ## making the background transparent below
    # fig.update_layout({
    # 'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    # 'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    # },
    # margin=dict(t=0, b=0, l=0, r=0)) 
    df['point_size'] = 10
    fig = px.scatter_mapbox(
        df[df['species'] ==  species],
        lat="decimalLatitude",
        lon="decimalLongitude",
        color="genericName",
        color_continuous_scale=px.colors.cyclical.IceFire,
        size = 'point_size',
        zoom=5,
        mapbox_style="open-street-map")

    fig.update_layout(showlegend=False) 
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })


    return fig


## function for creating the treemap to show specific point wise values 
def create_cards(df, query=None):
    if query:
        ## filter the dataframe to the selected point
        df = df.query(query)
        df = pd.melt(df, value_vars=['avg_radiance', 'is_invasive', 'avg_deg_urban'])
        fig = px.treemap(df, path=['variable'], values='value')
        fig.data[0].textinfo = 'label+value'

        level = 1 # write the number of the last level you have
        lvl_clr = "#5cb25d"
        font_clr = "black"

        fig.data[0]['marker']['colors'] =[lvl_clr for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]
        fig.data[0]['textfont']['color'] = [font_clr  for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]

        fig.data[0]['textfont']['size'] = 30
        return  fig

## function for creating the treemap to show specific point wise values 
def create_trends(df, query=None):
    if query:
        ## filter the dataframe to the selected point
        df = df.query(query)
        
        start = dt.datetime(2018, 1, 1)
        end = dt.datetime(2018, 12, 31)

        # Create Point for Vancouver, BC
#         pt = Point(df.loc[0,'decimalLatitude'], df.loc[0,'decimalLongitude'], 0)
        pt = Point(53.033981, -1.380991, 0)

        # Get daily data for 2018
        data = Daily(pt, start, end)
        data = data.fetch().reset_index(level=0)
        if data.shape[0] > 0:
            fig = px.line(data, x='time', y='tavg', template='plotly_white',
                          title='Climate Covariates')
            fig.update_layout(width=600)
            return  fig
        
        
### placeholder histogram plot of species counts
def species_counts(df=df):
    fig = px.histogram(df, y="species",color_discrete_sequence=['#5cb25d'])
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return fig


################################ Book keeping functions (species filter and call back on click)

## function to update species filter based on selection in country
@pn.depends(country.param.value, watch=True)
def _update_species(country):
    start = start_date.value.strftime('%Y-%m-%d')
    end = end_date.value.strftime('%Y-%m-%d')
    sql = f"""
    SELECT
        DISTINCT species
    FROM `gbif-challenge.airflow_uploads.gbif_combined`
    WHERE DATE(eventDate) BETWEEN "{start}" AND "{end}"
    AND country in ("{country}")
    """
    bq = client.query(sql).to_dataframe() ###add error checking
    if len(bq) > 0:
        species.options = list(bq.species)
        species.value = list(bq.species)[0]
    else: ## adding a popup box when no data is found for query. 
        template.open_modal()
        
## create the world scatter plot
plot_scatter = pn.pane.Plotly(occ_plot(species=species.value),width= 1050, height= 550)
        
## dependent hidden function to run when a point is clicked in the plot_scatter
@pn.depends(plot_scatter.param.click_data, watch=True)
def _update_after_click_on_1(click_data):
    if click_data !=None:
        lat = click_data['points'][0]['lat']
        lon = click_data['points'][0]['lon']
        plot_cards.object = create_cards(df, f'decimalLatitude == {lat}')
        
## function to download dataframe when button is pressed
def get_csv():
    return BytesIO(df.to_csv().encode())


###################### Main functions to query bigquery and update plots on click 

## function to get bigquery data, only works for event date filter for now
def query(start="2022-04-04", end="2022-06-04", country='Brazil', species = 'Callicore sorana'):
    sql = f"""
    SELECT
        *
    FROM `gbif-challenge.airflow_uploads.gbif_combined`
    WHERE DATE(eventDate) BETWEEN "{start}" AND "{end}"
    AND country in ("{country}")
    """
    bq = client.query(sql).to_dataframe() 
    return bq

    
## function to run when update button is pressed
def fetch_data(input):
    global df, cols
    if button.clicks > 0:
        bq = query(start_date.value.strftime('%Y-%m-%d'), 
                   end_date.value.strftime('%Y-%m-%d'),
                   country.value,
                   species.value) 
        if len(bq) > 0:
            df = bq.copy()
            plot_scatter.object = occ_plot(df)
            plot_cards.object = create_cards(df, f"decimalLatitude == {df.loc[0,'decimalLatitude']}")
            plot_trends.object = create_trends(df, f"decimalLatitude == {df.loc[0,'decimalLatitude']}")

            plot_species.object = species_counts(df)
            display_data.value = df[cols]
        else: ## adding a popup box when no data is found for query. 
            template.open_modal()
            time.sleep(10) ## do we need to close it ourselves?
            template.close_modal()


########################instantations of all panes required to display


###instantiate the cards plot
plot_trends = pn.pane.Plotly(create_trends(df, f'decimalLatitude == -22.258903'), width=400, height=400)

## species count histogram instantiate
plot_species = pn.pane.Plotly(species_counts())

###instantiate the cards plot
plot_cards = pn.pane.Plotly(create_cards(df, f'decimalLatitude == -22.258903'), width=400, height=400)

## display data, can delete later
cols = ['decimalLatitude','decimalLongitude', 'eventDate', 'species']
display_data = pn.widgets.DataFrame(df[cols].head(20))

## file download button
file_download_csv = pn.widgets.FileDownload(filename="gbif_covariates.csv", callback=get_csv, button_type="primary")

###what function to run when update buttton is pressed
button.on_click(fetch_data)



############## The main template to render, sidebar for text

template = pn.template.FastGridTemplate(
    title="🌏 GBIF Powered by Covariates",
    header = ['<a href="https://github.com/tekritesh/bio-conservation/tree/main">About</a>'],
    sidebar=["""We are interested bleh bleh bleh.\n We will hunt you down if you harm ANY flora or fauna."""],
    accent = '#5cb25d', sidebar_width = 280, background_color = '#f5f5f5',
    neutral_color = '#ffffff',
    corner_radius = 15,
    modal = ["## No data for chosen filters. Please choose a different combination of parameters"]
)

############## specify which portion of the main page grid you want to place a plot in

template.main[:1, :] = pn.Row(pn.Column(start_date, end_date),
                              country,
                              species,
                              button)

template.main[1:5, :]=pn.Tabs(('GBIF',pn.Column(plot_scatter)),
                              ('Radiance', pn.pane.HTML(HTML('map1.html'), width=600)), dynamic=True)

template.main[5:9, :4] = pn.Column(plot_cards)

template.main[5:9, 6:12]= pn.Column('### Species Counts', plot_species, height=400)
template.main[9:11, :]= pn.Column(file_download_csv, display_data, height=400)

template.main[11:13, :] = pn.Column(plot_trends)


###color examples
##77cb
#'#faad55'
#'#f0a3bc'
#a18dd6


## tells the terminal command to run the template variable as a dashboard

template.servable();