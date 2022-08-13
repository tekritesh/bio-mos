import os
from click import style 
import pandas as pd
import numpy as np
import datetime as dt
import time
from io import BytesIO
from IPython.display import HTML
from ipyleaflet import LegendControl
from math import pi, cos

import panel as pn
import param
import plotly.express as px
import plotly.graph_objects as go
from meteostat import Point, Daily

from google.cloud import bigquery

import ee
import geemap.geemap as geemap

#CSS
css = '''
.bk.update_plot_button_custom {
  margin-top: 20px !important;
}
.bk.update_map_button_custom {
  margin-top: 20px !important;
}
'''

pn.config.raw_css.append('''
#content {
background-color: #d9d1bb !important;
}
''')

pn.extension(raw_css=[css], 
            css_files = ['https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css',
                         'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css'],
            js_files={'bootstrap_popper': 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js'})

service_account = '292293468099-compute@developer.gserviceaccount.com'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../gcp_keys.json" ## ritesh computer
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "gbif-challenge-deed5b20a659.json" ##advika computer
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/mnt/.cred/gbif-challenge-a41b66fe5446.json" ##our vm

credentials = ee.ServiceAccountCredentials(service_account, "../gcp_keys.json") ##ritesh advika
#credentials = ee.ServiceAccountCredentials(service_account, 'gbif-challenge-deed5b20a659.json')
#credentials = ee.ServiceAccountCredentials(service_account, '/mnt/.cred/gbif-challenge-a41b66fe5446.json') ###our vm
ee.Initialize(credentials)

client = bigquery.Client()


df = pd.read_csv('gbif_combined.csv')
# df = pd.read_csv("/Users/riteshtekriwal/Work/Data/Raw/bio-conservation/test_combined.csv")


################################## All the filter widgets we need
start_date = pn.widgets.DatePicker(name='Start Date', start = dt.date(2021, 12, 1),
                                  end=dt.date(2022, 4, 30), value = dt.date(2022, 4, 4), height=50, width=200)

end_date = pn.widgets.DatePicker(name='End Date', start = dt.date(2021, 12, 1),
                                  end=dt.date(2022, 4, 30), value = dt.date(2022, 4, 5), height=50, width=200)

country = pn.widgets.Select(name='Country', options=['United Kingdom of Great Britain and Northern Ireland','Brazil'], 
                            value = 'United Kingdom of Great Britain and Northern Ireland' , width=500)
species = pn.widgets.Select(name='Select Species',
                             options=list(df.groupby('species').key.count().\
                                reset_index(name='count').sort_values(['count'], ascending=False).species),
                             width = 300)
                             
button = pn.widgets.Button(name='Fetch Data', width= 300,height = 40,button_type='primary', css_classes=['update_plot_button_custom'])

button_map = pn.widgets.Button(name='Update Map', width= 200,height = 30, button_type='primary', css_classes=['update_map_button_custom'])


##################################### All our plot functions

## the world map view of occurrence data
def occ_plot(df=df, species='Anemone nemorosa'):

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

    return fig

# Generate a landcover background
def create_land_cover_map(start_date="2021-12-01", end_date="2022-05-01", df=df):
    df_temp = df.rename(columns={'decimalLatitude': 'latitude', 'decimalLongitude': 'longitude'})
    df_temp = df_temp[['latitude', 'longitude', 'species']]
    repeat_df = pd.DataFrame(np.repeat(df_temp.values, 2, axis=0))
    repeat_df.columns = df_temp.columns
    latitude = repeat_df.latitude.values[0]
    longitude = repeat_df.longitude.values[0]

    #bounding box
    r_earth = 6371000.0
    displacement = 100
    latitude_max = latitude + (displacement / r_earth) * (180 / pi)
    longitude_max = longitude + (displacement / r_earth) * (180 / pi) / cos(latitude * pi / 180)

    latitude_min = latitude - (displacement / r_earth) * (180 / pi)
    longitude_min = longitude - (displacement / r_earth) * (180 / pi) / cos(latitude * pi / 180)
    region = ee.Geometry.BBox(longitude_min, latitude_min, longitude_max, latitude_max)
    
    dw = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterDate(start_date, end_date).filterBounds(region).mode()
    classification = dw.select('label')
    dwVisParams = {'min': 0, 'max': 8, 'palette': [
    '#526983', '#68855c', '#88B053', '#526983', '#8C785C', '#726f4c',
    '#af6457', '#d8af6b', '#526983']}
    map1 = geemap.Map()

    map1.add_basemap('TERRAIN')
    map1.setCenter(longitude, latitude, 12)
    map1.addLayer(classification, dwVisParams, 'Classified Image', opacity= 0.8)
    map1.add_points_from_xy(repeat_df, popup=['species', 'latitude', 'longitude'], x='longitude', y='latitude',
                             layer_name='marker')
    legend = LegendControl({
        "Water":"#526983",
        "Trees":"#68855c",
        "Grass":"#88B053",
        "Flooded Vegetation":"#526983",
        "Crops":"#8C785C",
        "Shrub & Scrub":"#726f4c",
        "Built Area":"#af6457",
        "Bare ground":"#d8af6b",
        "Snow & Ice":"#526983"},
        name="")
    
    map1.add_control(legend)
    map1.remove_drawn_features()

    return map1.to_html(width='100%', height='400px')

## function to return values for display cards panel    
def create_display(df):
    df = df.reset_index()
    if len(df) > 0:
        return round(df.loc[0,'avg_deg_urban'],2), round(df.loc[0, 'avg_radiance'],2), \
            df.loc[0, 'tavg'], df.loc[0,'wspd'], df.loc[0,'prcp']

## function for creating the treemap to show specific point wise values 
def create_cards(df):

    df = pd.melt(df, value_vars=['snow','wdir','wspd','wpgt','pres','tsun'])
    if len(df) ==0:
        df = pd.read_csv('weather.csv')
    #  Refer: https://dev.meteostat.net/formats.html#meteorological-parameters
    variable_names = {'snow':'Snow Depth(mm)',
        'wdir':'Wind Direction(deg)',
        'wspd':'Wind Speed(km/hr)',
        'wpgt':'Wind Peak Gust(km/hr)',
        'pres':'Precipitation(mm)',
        'tsun':'Sunshine Duration(mins)'}
    
    # df = df.replace({"variable":variable_names})
 
    fig = px.treemap(df, path=['variable'], values='value')
    fig.data[0].textinfo = 'label+value'

    level = 1 # write the number of the last level you have
    lvl_clr = "#9C9C5E"
    font_clr = "black"

    fig.data[0]['marker']['colors'] =[lvl_clr for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]
    fig.data[0]['textfont']['color'] = [font_clr  for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]
    fig.data[0]['textfont']['size'] = 40

    fig.update_layout(
        title='Weather Stats for <Date> & [lat/lng]',
        autosize=False,
        hovermode='closest',
        margin={"r":0,"t":100,"l":0,"b":0},
        template="plotly_white",
        showlegend=True)

    return fig

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

        
## histogram plot of species counts
def species_counts(df=df, country = 'United Kingdom of Great Britain and Northern Ireland', start = '2022-04-04', end='2022-04-05'):
    df_temp = df['species'].value_counts().rename_axis('Species').reset_index(name='Occurrence Count')
    df_temp = df_temp.sort_values(by = ['Occurrence Count'],ascending=[False])
    
    if country == 'United Kingdom of Great Britain and Northern Ireland':
        short_name = 'United Kingdom'
    else:
        short_name = country

    fig = px.bar(
        df_temp.head(10),
        x = 'Occurrence Count',
        y = "Species",
        color="Species",
        color_discrete_sequence=
        # px.colors.cyclical.IceFire,
        px.colors.qualitative.Antique,
        text = 'Occurrence Count',
        title = f'Species Occurrences for {short_name}'
    )
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

    return fig

## Function for invasive species count
def invasive_species_counts(df=df):
    df_temp = df[df['is_invasive'] == True]  
    if not df_temp.empty:
        title = 'Invasive-Species Occurrence Distribution'
    else:
        title = 'No Invasive Species Found for the country and date selected'
    fig = px.histogram(df_temp, y="species",
                    category_orders=dict(species=list(df_temp.species.unique())),
                    title = title,
                    color='species',
                    labels=dict(species='Species'),
                    template="plotly_white",
                    color_discrete_sequence=px.colors.qualitative.Antique
                    )
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    
    return fig

## Climate timeseries trends 
def create_trends(df):
        
        start = dt.datetime(2021, 6, 1)
        end = dt.datetime(2022, 6, 1)

        df = df.reset_index()
        pt = Point(df.loc[0,'decimalLatitude'], df.loc[0,'decimalLongitude'], 0)
        #pt = Point(53.033981, -1.380991, 0)

        data = Daily(pt, start, end)
        data = data.fetch().reset_index(level=0)
        if len(data) > 0:
            data = pd.melt(data,value_vars=['tavg', 'tmin', 'tmax'],id_vars=['time'])

            if data.shape[0] > 0:
                variable_names = {
                    'tavg': 'Avg',
                    'tmin': 'Min',
                    'tmax': 'Max',
                }
                data = data.replace({"variable":variable_names})
                # data.rename(columns = {'variable':'Climate Variable', 'value':'Temp(C)'}, inplace = True)


                fig = px.line(
                    data,
                    x='time',
                    y='value',
                    color='variable',
                    color_discrete_sequence=px.colors.qualitative.Antique,
                    template='plotly_white',
                    title=f"Climate Covariates for [Lat,Lng]: [{df.loc[0,'decimalLatitude']}, {df.loc[0,'decimalLongitude']}]",
                    labels=dict(variable="Climate Variable", value="Temp(C)",time='Date')
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
        else: 
            fig_nan = go.Figure()
            fig_nan.update_layout(title="No data found for the chosen point", template='plotly_white')
            return fig_nan


################################ Book keeping functions (species filter and call back on click)
        
## create the world scatter plot
plot_scatter = pn.pane.Plotly(occ_plot(species=species.value),width= 700, height= 500)
        
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
        plot_land_cover.object = create_land_cover_map(df=df_temp)
        disp_deg_urban.value, disp_radiance.value, disp_avg_temp.value,\
            disp_wind_speed.value, disp_precipitation.value= create_display(df_temp)
        
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
            disp_deg_urban.value, disp_radiance.value, disp_avg_temp.value,\
                 disp_wind_speed.value, disp_precipitation.value, disp_wind_dir.value = create_display(df_temp)

            plot_species.object = species_counts(df, country.value, start, end)
            display_data.value = df[cols]

            #update land cover
            plot_land_cover.object = create_land_cover_map(df=df_temp)
            # update invasive species graph
            plot_invasive_species.object = invasive_species_counts(df)

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
###initial conditions
df_initial = df[(df.decimalLatitude == 51.458686) & (df.decimalLongitude == 0.073012)].head(1).copy()

###instantiate the cards plot
plot_trends = pn.pane.Plotly(create_trends(df_initial), width=1450, height=450)

## species count histogram instantiate
plot_species = pn.pane.Plotly(species_counts(),  height=600, width=625)

#invasice species plot
plot_invasive_species = pn.pane.Plotly(invasive_species_counts(df),  height=400,width=625)

###instantiate the cards plot
plot_cards = pn.pane.Plotly(create_cards(df_initial), width=600, height=400)

###instantiate the pie plot
plot_pie = pn.pane.Plotly(create_pie(df_initial), width=600, height=450)

plot_land_cover = pn.pane.HTML(HTML(create_land_cover_map(df=df_initial)), width = 680)

## display data, can delete later
cols = [ 'species','eventDate','decimalLatitude','decimalLongitude','is_invasive','avg_radiance',
         'land_cover_label', 'tavg', 'tmin', 'tmax', 'prcp','snow','wdir','wspd','phh2o_0_5cm_mean',
        'clay_0_5cm_mean','nitrogen_0_5cm_mean' ]
display_data = pn.widgets.DataFrame(df[cols].head(9), width=1450)

## file download button
file_download_csv = pn.widgets.FileDownload(filename="gbif_covariates.csv", callback=get_csv, button_type="primary")

###what function to run when update button is pressed
button.on_click(fetch_data)

###what function to run when update button is pressed
button_map.on_click(update_map)

#instantiate display
info_urban = pn.pane.HTML("""<a href="#" data-toggle="tooltip" title="Average degree of Urbanization"><i class="bi-info-circle"></i></i></a>""", width=85)
info_radiance = pn.pane.HTML("""<a href="#" data-toggle="tooltip" title="Average Radiance value measured in lumens"><i class="bi-info-circle"></i></i></a>""", width=85)
info_temp = pn.pane.HTML("""<a href="#" data-toggle="tooltip" title="Average Temperature (C°)"><i class="bi-info-circle"></i></i></a>""", width=85)
info_wind_speed = pn.pane.HTML("""<a href="#" data-toggle="tooltip" title="Wind Speed in m/s"><i class="bi-info-circle"></i></i></a>""", width=85)
info_precipitation = pn.pane.HTML("""<a href="#" data-toggle="tooltip" title="Rainfall in cm"><i class="bi-info-circle"></i></i></a>""", width=85)

disp_deg_urban = pn.indicators.Number(
    name='Deg Urban', value=2.9, format='{value}', font_size ='32pt', 
    colors=[(33, '#68855C'), (66, '#D9AF6B'), (100, '#855C75')], width=121)

disp_radiance = pn.indicators.Number(
    name='Radiance', value=24.8, format='{value}', font_size ='32pt', 
    colors=[(33, '#68855C'), (66, '#D9AF6B'), (100, '#855C75')], width=100)

disp_avg_temp = pn.indicators.Number(
    name='Avg Temp', value=12.4, format='{value}C', font_size ='32pt',

    colors=[(25, '#68855C'), (35, '#D9AF6B'), (40, '#855C75')], width=110)

disp_wind_speed = pn.indicators.Number(
    name='Wind Speed', value=23, format='{value}mps', font_size ='32pt', 
    colors=[(2, '#68855C'), (5, '#D9AF6B'), (15, '#855C75')], width=140)

disp_precipitation = pn.indicators.Number(
    name='Precipitation', value=0.2, format='{value}mm', font_size ='32pt', 
    colors=[(33, '#68855C'), (66, '#D9AF6B'), (100, '#855C75')], width=130)


############## The main template to render, sidebar for text

template = pn.template.FastGridTemplate(
    title="GBIF Powered by Covariates",
    header = [pn.Column('','<a href="https://github.com/tekritesh/bio-conservation/tree/main">About</a>')],
    # sidebar=["""We are interested bleh bleh bleh.\n We will hunt you down if you harm ANY flora or fauna."""],
    accent = '#4f6457',
    sidebar_width = 280,
    background_color = '#f5f5f5',
    # favicon = 'https://img.icons8.com/external-flaticons-lineal-color-flat-icons/452/external-earth-plants-flaticons-lineal-color-flat-icons-2.png',
    favicon = 'https://img.icons8.com/external-icongeek26-linear-colour-icongeek26/452/external-earth-zoology-icongeek26-linear-colour-icongeek26.png',
    # background_color = '#f7f4eb',
    theme_toggle = False,
    neutral_color = '#ffffff',
    corner_radius = 15,
    modal = ["## No data for chosen filters. Please choose a different combination of parameters"]
)

############## specify which portion of the main page grid you want to place a plot in

#sidebar
# operating_instruction = pn.pane.Markdown(""" # Operating Instruction:
#                                         """, width=200, height=3000)
template.main[0:18, 0:2] = pn.Column(
    pn.Column(
        "## Hello Earth Dwellers",
        pn.Column("""We are interested in integrating and visualizing environmental variables like climate, soil, and 
                                        human interference data alongside the biodiversity data from GBIF. Here you can visualize, query, and download
                                         the data to further conduct analyses on our precious but dwindling biodiversity.""", width = 260),
                                            pn.pane.JPG('https://i.pinimg.com/originals/4f/13/08/4f130877108da46e7159b71beaf294a7.jpg', width=500, height = 500, margin=(0,0,0,15)),
                                            pn.pane.JPG('https://i.pinimg.com/originals/4f/13/08/4f130877108da46e7159b71beaf294a7.jpg', width=500, height = 500, margin=(25,0,0,-250)),
                                            # operating_instruction
                                            ), sizing_mode='stretch_both', height=3000, width=210)

# static_text = pn.widgets.StaticText(name='Static Text', value='A string', width = 200)
# template.main[:1, 2:] = pn.Column(static_text,pn.Row(start_date, end_date, country, button, height=10))

template.main[:1, 2:] = pn.Column("",pn.Row(start_date, end_date, country, button, height=10))

template.main[1:5, 7:12]=pn.Column(pn.Row(species,button_map), plot_scatter)

template.main[1:5, 2:7]= pn.Column(plot_species, height=400)

template.main[5:6, 2:4] = pn.Row(pn.Row(disp_deg_urban, info_urban))
template.main[5:6, 4:6] = pn.Row(pn.Row(disp_radiance, info_radiance))
template.main[5:6, 6:8] = pn.Row(pn.Row(disp_avg_temp, info_temp))
template.main[5:6, 8:10] = pn.Row(pn.Row(disp_precipitation, info_precipitation))
template.main[5:6, 10:12] = pn.Row(pn.Row(disp_wind_speed, info_wind_speed))


template.main[6:9, 2:7] = pn.Column(plot_pie)

template.main[6:9, 7:12] = pn.Column(plot_cards)

template.main[9:12, 2:12] = pn.Column(plot_trends)

template.main[12:15, 2:7] = pn.Column(plot_invasive_species)

# template.main[12:15, 8:12] = pn.Column(plot_land_cover, height=200, width = 200)

land_cover_title = pn.pane.HTML("""Land Cover Classification Labels""",
style={'padding-left': '190px', 'font-size': '16px'}, width=500)
template.main[12:15, 7:12] = pn.Column(land_cover_title, plot_land_cover, width = 500)


#static_text = pn.widgets.StaticText(name='Land Cover', value='', width = 200)
# template.main[:1, 2:] = pn.Column(static_text,pn.Row(start_date, end_date, country, button, height=10))
#template.main[12:15, 7:12] = pn.Column(static_text,plot_land_cover)

template.main[15:18, 2:12]= pn.Column(file_download_csv, display_data)

## tells the terminal command to run the template variable as a dashboard
template.servable();