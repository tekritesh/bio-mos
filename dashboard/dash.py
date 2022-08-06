import os 
import pandas as pd
import numpy as np
import datetime as dt
import time
# import ee
# import geemap as geemap
from io import BytesIO
from IPython.display import HTML
from ipyleaflet import LegendControl

import panel as pn
import param
import plotly.express as px
import plotly.graph_objects as go
#from wordcloud import WordCloud
from meteostat import Point, Daily

from google.cloud import bigquery

import ee
import geemap.geemap as geemap

service_account = '292293468099-compute@developer.gserviceaccount.com'

#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../gcp_keys.json" ## ritesh computer
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "gbif-challenge-deed5b20a659.json" ##advika computer
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/mnt/.cred/gbif-challenge-a41b66fe5446.json" ##our vm

#credentials = ee.ServiceAccountCredentials(service_account, 'gbif-challenge-deed5b20a659.json') ##ritesh advika
credentials = ee.ServiceAccountCredentials(service_account, '/mnt/.cred/gbif-challenge-a41b66fe5446.json') ###our vm
ee.Initialize(credentials)

client = bigquery.Client()


df = pd.read_csv('gbif_combined.csv')
# df = pd.read_csv("/Users/riteshtekriwal/Work/Data/Raw/bio-conservation/test_combined.csv")


################################## All the filter widgets we need
start_date = pn.widgets.DatePicker(name='Start Date', start = dt.date(2021, 12, 1),
                                  end=dt.date(2022, 4, 30), value = dt.date(2022, 4, 4))

end_date = pn.widgets.DatePicker(name='End Date', start = dt.date(2021, 12, 1),
                                  end=dt.date(2022, 4, 30), value = dt.date(2022, 4, 5))

country = pn.widgets.Select(name='Country', options=['United Kingdom of Great Britain and Northern Ireland','Brazil'], 
                            value = 'United Kingdom of Great Britain and Northern Ireland' )
species = pn.widgets.Select(name='Species',
                             options=list(df.groupby('species').key.count().\
                                reset_index(name='count').sort_values(['count'], ascending=False).species),
                             width = 300)
                             
button = pn.widgets.Button(name='Update Plots', width= 200, button_type='primary')

button_map = pn.widgets.Button(name='Update Map', width= 200, button_type='primary')


##################################### All our plot functions

## the world map view of occurrence data
def occ_plot(df=df, species='Anemone nemorosa'):
    # fig = px.scatter_geo(df, lat="decimalLatitude", lon='decimalLongitude', color='species')
    # ## making the background transparent below
    # fig.update_layout({
    # 'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    # 'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    # },
    # margin=dict(t=0, b=0, l=0, r=0)) 

    df = df[df.species == species].copy()
    df['point_size'] = 10
    # df['date'] = df['eventDate'].str[:10]
    df['date']=df['eventDate'].to_string(index=False)[:10]
    fig = px.scatter_mapbox(
        df,
        lat="decimalLatitude",
        lon="decimalLongitude",
        #color="land_cover_label",
        hover_name= 'genericName',
        size = 'point_size',
        hover_data= ['species','decimalLongitude','decimalLatitude', 'date'],
        # hover_data= ['species','decimalLongitude','decimalLatitude'],
        # color_discrete_sequence=['#5cb25d'],
        # color_discrete_sequence=px.colors.qualitative.Bold,
        color_discrete_sequence=px.colors.qualitative.Antique,
        # color_continuous_scale=px.colors.cyclical.IceFire,
        zoom=6,
        mapbox_style="open-street-map")

    # fig.update_layout(showlegend=False) 
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })

    fig.update_layout(
        # title='Geo Spatial Occcurence Instances for <>',
        autosize=True,
        hovermode='closest',
        margin={"r":0,"t":0,"l":0,"b":0},
        template="plotly_white",
        showlegend=False)

    # fig.update_layout(
    #     updatemenus=[
    #         dict(
    #             type = "buttons",
    #             direction = "left",
    #             buttons=list([
    #                 dict(
    #                     args=["color",'#ffffff'],
    #                     label="Occurence",
    #                     method="update"
    #                 ),
    #                 dict(
    #                     args=["color", "#aaaaaa"],
    #                     label="Soil",
    #                     method="update"
    #                 )
    #             ]),
    #             pad={"r": 10, "t": 10},
    #             showactive=True,
    #             x=0.11,
    #             xanchor="left",
    #             y=1.1,
    #             yanchor="top"
    #         ),
    #     ]
    # )

    # Add annotation
    # fig.update_layout(
    #     annotations=[
    #         dict(text="Trace type:", showarrow=False,
    #                             x=0, y=1.06, yref="paper", align="left")
    #     ]
    # )

    return fig

# Generate a landcover background
def create_land_cover_map(latitude=51.458686, longitude=0.073012, start_date="2021-12-01", end_date="2022-05-01"):
    region = ee.Geometry.BBox(-179, -89, 179, 89)
    dw = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterDate(start_date, end_date).filterBounds(region).mode()
    classification = dw.select('label')
    dwVisParams = {'min': 0, 'max': 8, 'palette': [
    '#419BDF', '#397D49', '#88B053', '#7A87C6', '#E49635', '#DFC35A',
    '#C4281B', '#A59B8F', '#B39FE1']}
    map1 = geemap.Map()
    map1.add_basemap('HYBRID')
    map1.setCenter(longitude, latitude, 11)
    map1.addLayer(classification, dwVisParams, 'Classified Image')
    legend = LegendControl({"Water":"#419BDF", "Trees":"#397D49", "Grass":"#88B053",
    "Flooded Vegetation":"#7A87C6", "Crops":"#E49635", "Shrub & Scrub":"#DFC35A",
    "Built Area":"#C4281B", "Bare ground":"#A59B8F", "Snow & Ice":"#B39FE1"}, name="Land Cover Plot Legend",
     position="bottomright")
    map1.add_control(legend)
    return map1.to_html(width='100%', height='450px')

# Generate a landcove background
def create_display(df):
    # filter the dataframe to the selected point
    df = df.reset_index()
    if len(df) > 0:
        return round(df.loc[0,'avg_deg_urban'],2), round(df.loc[0, 'avg_radiance'],2), \
            df.loc[0, 'tavg'], df.loc[0,'wspd'], df.loc[0,'prcp']

## function for creating the treemap to show specific point wise values 
def create_cards(df):
    df = pd.melt(df, value_vars=['tavg', 'tmin', 'tmax','prcp','wspd','wdir'])
    if len(df) ==0:
        df = pd.read_csv('weather.csv')
    fig = px.treemap(df, path=['variable'], values='value')
    fig.data[0].textinfo = 'label+value'
    

    level = 1 # write the number of the last level you have
    lvl_clr = "#9C9C5E"
    font_clr = "black"

    fig.data[0]['marker']['colors'] =[lvl_clr for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]
    fig.data[0]['textfont']['color'] = [font_clr  for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]

    fig.data[0]['textfont']['size'] = 40

    fig.update_layout(
        # title='Geo Spatial Occcurence Instances for <>',
        autosize=True,
        hovermode='closest',
        margin={"r":0,"t":0,"l":0,"b":0},
        template="plotly_white",
        showlegend=False)

    return fig

# ## function for creating the wordcloud to show specific point wise values 
# def create_wordcloud(df):
#     df = df.head(1)
#     df = pd.melt(
#         df.head(1),
#         value_vars=[
#             'land_cover_label',
#             'snow',
#             'is_invasive',
#             'species',
#             'country'])
#     df['count']=[1,1,1,1,1]
#     df['Title']= df['variable'].astype(str) +":" +df['value'].astype(str)

#     df=df[['Title','count']]

#     d = {a: x for a, x in df.values}
#     wc = WordCloud(
#         background_color='white',
#         # font_path= ,
#         colormap='tab20b',
#         prefer_horizontal = 1,
#         min_font_size=10,
#         scale=1,
#         # background_color = 
#         width=400,
#         height=500)
#     wc.fit_words(d)
#     fig = wc.to_image()

#     return fig

## function for creating the pie chart for soil
def create_pie(df):   
    if len(df) == 0:
        df = pd.read_csv("soil_temp.csv")

    else:
    # Standardizing Units to g/Kg
        df['soc_0_5cm_mean']=df['soc_0_5cm_mean']*0.10
        df['nitrogen_0_5cm_mean']=df['nitrogen_0_5cm_mean']*0.01

        df = pd.melt(
                    df.head(1),
                    value_vars=['clay_0_5cm_mean',
                                'silt_0_5cm_mean',
                                'sand_0_5cm_mean',
                                'soc_0_5cm_mean',
                                'nitrogen_0_5cm_mean']
                    )

        df['variable']=df['variable'].replace({
            'clay_0_5cm_mean':'clay %',
            'silt_0_5cm_mean':'silt %',
            'sand_0_5cm_mean':'sand %',
            'soc_0_5cm_mean':'organic carbon %',
            'nitrogen_0_5cm_mean':'nitrogen %',          
        })

    fig = px.pie(
        df,
        values='value',
        names='variable',
        title='Soil Compositon %',
        color_discrete_sequence=px.colors.qualitative.Antique,
        # px.colors.sequential.Greens_r,
        hole=.3)
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    return fig

        
### placeholder histogram plot of species counts
def species_counts(df=df, country = 'United Kingdom of Great Britain and Northern Ireland', start = '2022-04-04', end='2022-04-05'):
    df_temp = df['species'].value_counts().rename_axis('Species').reset_index(name='Occurrence Count')
    df_temp = df_temp.sort_values(by = ['Occurrence Count'],ascending=[False])
    
    fig = px.bar(
        df_temp.head(10),
        x = 'Occurrence Count',
        y = "Species",
        color="Species",
        color_discrete_sequence=
        # px.colors.cyclical.IceFire,
        px.colors.qualitative.Antique,
        text = 'Occurrence Count',
        title = f'Species Occurrences for {country} between {start} and {end}'
    )
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

    return(fig)

#Function for invasive species count
def invasive_species_counts(df=df):
    # df=  df[df['country'] == 'Brazil']

    fig = px.histogram(df, x="species",
                       category_orders=dict(species=list(df.species.unique())),
                       title = f'Invasive Species Occurrences Histogram',
                       color='species',
                       color_discrete_sequence=px.colors.qualitative.Antique
                       )
    return(fig)

#Climate timeseries trends 
def create_trends(df):
        
        start = dt.datetime(2021, 6, 1)
        end = dt.datetime(2022, 6, 1)

        # start = start_date.value.strftime('%Y-%m-%d')
        # end = end_date.value.strftime('%Y-%m-%d')

        # Create Point for Vancouver, BC
        df = df.reset_index()
        pt = Point(df.loc[0,'decimalLatitude'], df.loc[0,'decimalLongitude'], 0)
        #pt = Point(53.033981, -1.380991, 0)

        # Get daily data for 2018
        data = Daily(pt, start, end)
        data = data.fetch().reset_index(level=0)
        if len(data) > 0:
        # data = pd.melt(data,value_vars=['tavg', 'tmin', 'tmax','prcp','wspd'],id_vars=['time'])
            data = pd.melt(data,value_vars=['tavg', 'tmin', 'tmax'],id_vars=['time'])

            if data.shape[0] > 0:
                fig = px.line(
                    data,
                    x='time',
                    y='value',
                    color='variable',
                    color_discrete_sequence=px.colors.qualitative.Antique,
                    template='plotly_white',
                    title=f"Climate Covariates for Latitude: {df.loc[0,'decimalLatitude']} and Longitude: {df.loc[0,'decimalLongitude']}"
                    )

                fig.update_layout(
                    # title='Geo Spatial Occcurence Instances for <>',
                    autosize=True,
                    hovermode='closest',
                    # margin={"t":0,"b":0},
                    showlegend=True)
                fig.add_vline(x=str(df.loc[0,'eventDate'])[:10], ##annotation did not work
                             line_width=1, line_dash="solid", line_color="black")

                # hide and lock down axes
                fig.update_xaxes(visible=True, fixedrange=True)
                fig.update_yaxes(visible=True, fixedrange=True)

                # remove facet/subplot labels
                fig.update_layout(annotations=[], overwrite=True)

                return  fig


################################ Book keeping functions (species filter and call back on click)
        
## create the world scatter plot
plot_scatter = pn.pane.Plotly(occ_plot(species=species.value),width= 700, height= 550)
        
## dependent hidden function to run when a point is clicked in the plot_scatter
@pn.depends(plot_scatter.param.click_data, watch=True)
def _update_after_click_on_1(click_data):
    if click_data !=None:
        lat = click_data['points'][0]['lat']
        lon = click_data['points'][0]['lon']
        ###only pass smaller filtered dataframe to click map point based plots
        df_temp = df[(df.decimalLatitude == lat) & (df.decimalLongitude == lon)].copy() ####need to update this query in the future
        plot_pie.object = create_pie(df_temp)
        plot_trends.object = create_trends(df_temp)
        plot_cards.object = create_cards(df_temp)
        #update land cover
        plot_land_cover.object = create_land_cover_map(latitude=lat, longitude=lon)
        # display_workcloud.object = create_wordcloud(df_temp)
        disp_deg_urban.value, disp_radiance.value, disp_avg_temp.value,\
            disp_wind_speed.value, disp_precipitation.value = create_display(df_temp)
        # plot_pie.object = create_cards(df, f'decimalLatitude == {lat}')
        
## function to download dataframe when button is pressed
def get_csv():
    return BytesIO(df.to_csv().encode())


###################### Main functions to query bigquery and update plots on click 

## function to get bigquery data, only works for event date filter for now
def query(start="2022-04-04", end="2022-06-04", country='Brazil'):
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
        start, end = start_date.value.strftime('%Y-%m-%d'), end_date.value.strftime('%Y-%m-%d')
        bq = query(start, end, country.value) 
        if len(bq) > 0:
            df = bq.copy()
            df_temp = df.head(1).copy()

            ##only show available species for the country and time range
            species_list = list(df.groupby('species').key.count().\
                    reset_index(name='count').sort_values(['count'], ascending=False).species)
            species.options = species_list
            species.value = species_list[0]

            ###update plot objects
            plot_scatter.object = occ_plot(df, species.value)
            plot_cards.object = create_cards(df_temp)
            plot_pie.object = create_pie(df_temp)
            plot_trends.object = create_trends(df_temp)
            # display_workcloud = create_wordcloud(df_temp)
            disp_deg_urban.value, disp_radiance.value, disp_avg_temp.value,\
                 disp_wind_speed.value, disp_precipitation.value = create_display(df_temp)

            plot_species.object = species_counts(df, country.value, start, end)
            display_data.value = df[cols]

            #update land cover
            plot_land_cover.object = create_land_cover_map(df_temp['decimalLatitude'].values[0],
                                                           df_temp['decimalLongitude'].values[0])

        else: ## adding a popup box when no data is found for query. 
            template.open_modal()
            time.sleep(10) ## do we need to close it ourselves?
            template.close_modal()

## function to run when map species button is pressed
def update_map(input):
    global df, cols
    if button_map.clicks > 0:
        plot_scatter.object = occ_plot(df, species.value)


########################instantations of all panes required to display
###need to change this later###########
df_initial = df[(df.decimalLatitude == 51.458686) & (df.decimalLongitude == 0.073012)].head(1).copy()
###instantiate the cards plot
plot_trends = pn.pane.Plotly(create_trends(df_initial), width=1500, height=450)

## species count histogram instantiate
plot_species = pn.pane.Plotly(species_counts())

#invasice species plot

df_temp = df[df['is_invasive'] == True]
if not df_temp.empty:
    plot_invasive_species = pn.pane.Plotly(invasive_species_counts(df_temp))
else:
    plot_invasive_species = pn.pane.HTML("""<h1>No invasive species found for the country and date range selected </h1>""",
     style={'font-size': 'large'})

###instantiate the cards plot
plot_cards = pn.pane.Plotly(create_cards(df_initial), width=700, height=400)

###instantiate the pie plot
plot_pie = pn.pane.Plotly(create_pie(df_initial), width=700, height=450)

plot_land_cover = pn.pane.HTML(HTML(create_land_cover_map()),width = 600)

## display data, can delete later
cols = [ 'species','eventDate','decimalLatitude','decimalLongitude','country']
display_data = pn.widgets.DataFrame(df[cols].head(13),autosize_mode='fit_viewport')

## file download button
file_download_csv = pn.widgets.FileDownload(filename="gbif_covariates.csv", callback=get_csv, button_type="primary")

###what function to run when update buttton is pressed
button.on_click(fetch_data)

###what function to run when update buttton is pressed
button_map.on_click(update_map)

#instantiate display

disp_deg_urban = pn.indicators.Number(
    name='Deg Urban', value=2.9, format='{value}', font_size ='32pt', 
    colors=[(33, '#68855C'), (66, '#D9AF6B'), (100, '#855C75')])

disp_radiance = pn.indicators.Number(
    name='Radiance', value=24.8, format='{value}', font_size ='32pt', 
    colors=[(33, '#68855C'), (66, '#D9AF6B'), (100, '#855C75')])

disp_avg_temp = pn.indicators.Number(
    name='Avg Temp', value=12.4, format='{value}C', font_size ='32pt',
    colors=[(25, '#68855C'), (35, '#D9AF6B'), (40, '#855C75')])

disp_wind_speed = pn.indicators.Number(
    name='Wind Speed', value=23, format='{value}mps', font_size ='32pt', 
    colors=[(2, '#68855C'), (5, '#D9AF6B'), (15, '#855C75')])

disp_precipitation = pn.indicators.Number(
    name='Precipitation', value=0.2, format='{value}mm', font_size ='32pt', 
    colors=[(33, '#68855C'), (66, '#D9AF6B'), (100, '#855C75')])

#instantiate wordcloud
# display_workcloud =  pn.pane.PNG(create_wordcloud(df_initial))


############## The main template to render, sidebar for text

template = pn.template.FastGridTemplate(
    title="🌏 GBIF Powered by Covariates",
    header = [pn.Column('','<a href="https://github.com/tekritesh/bio-conservation/tree/main">About</a>')],
    # sidebar=["""We are interested bleh bleh bleh.\n We will hunt you down if you harm ANY flora or fauna."""],
    accent = '#6db784',
    sidebar_width = 280,
    background_color = '#f5f5f5',
    theme_toggle = False,
    neutral_color = '#ffffff',
    corner_radius = 15,
    modal = ["## No data for chosen filters. Please choose a different combination of parameters"]
)

############## specify which portion of the main page grid you want to place a plot in

template.main[:1, :] = pn.Row(pn.Column(start_date, end_date),
                              country,
                              pn.Column('',button))


# template.main[1:5, 6:12]=pn.Tabs(('GBIF',pn.Column(plot_scatter)),
#                               ('Radiance', pn.pane.HTML(HTML('map1.html'), width=600)), dynamic=True)

template.main[1:5, 6:12]=pn.Column(pn.Row(species,button_map), plot_scatter)


template.main[1:5,:6]= pn.Column(plot_species, height=400)


template.main[5:6, :] = pn.Row(
    disp_deg_urban,
    disp_radiance,
    disp_avg_temp,
    disp_precipitation,
    disp_wind_speed
    ) 
# template.main[5:6, :] = pn.Row(display_stickers)


template.main[6:9, :6] = pn.Column(plot_pie)

template.main[6:9, 6:12] = pn.Column(plot_cards)


template.main[9:12, :] = pn.Column(plot_trends)

template.main[12:15, :7]= pn.Column(file_download_csv, display_data, height=200, width = 200)

# template.main[12:15, 8:12] = pn.Column(display_workcloud)

# template.main[12:15, 8:12] = pn.Column(plot_land_cover, height=200, width = 200)
template.main[12:15, 7:12] = pn.Column(plot_land_cover, width = 600)

template.main[15:18, 0:6] = pn.Column(plot_invasive_species, width=600)


## tells the terminal command to run the template variable as a dashboard

template.servable();