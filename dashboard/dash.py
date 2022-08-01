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
from wordcloud import WordCloud


from meteostat import Point, Daily

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../gcp_keys.json" ##change this
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "gbif-challenge-deed5b20a659.json" ##change this
# df = pd.read_csv("test_combined.csv")


from google.cloud import bigquery

client = bigquery.Client()


# df = pd.read_csv('gbif_combined.csv')
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
def occ_plot(df=df, species='Callicore sorana'):
    # fig = px.scatter_geo(df, lat="decimalLatitude", lon='decimalLongitude', color='species')
    # ## making the background transparent below
    # fig.update_layout({
    # 'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    # 'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    # },
    # margin=dict(t=0, b=0, l=0, r=0)) 

    # Refer: https://plotly.com/python/custom-buttons/#methods


    df = df[df.species == species].copy()
    df['point_size'] = 10
    fig = px.scatter_mapbox(
        df,
        lat="decimalLatitude",
        lon="decimalLongitude",
        # color="genericName",
        hover_name= 'genericName',
        size = 'point_size',
        hover_data= ['species','decimalLongitude','decimalLatitude'],
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

    fig.update_layout(
        updatemenus=[
            dict(
                type = "buttons",
                direction = "left",
                buttons=list([
                    dict(
                        args=["color",'#ffffff'],
                        label="Occurence",
                        method="update"
                    ),
                    dict(
                        args=["color", "#aaaaaa"],
                        label="Soil",
                        method="update"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.11,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )

    # Add annotation
    fig.update_layout(
        annotations=[
            dict(text="Trace type:", showarrow=False,
                                x=0, y=1.06, yref="paper", align="left")
        ]
    )

    return fig
# Generate a landcover background
def create_land_cover_bg(df, query=None):
    if query:
        # filter the dataframe to the selected point
        df = df.query(query)
        df = pd.melt(df, value_vars=['tavg', 'tmin', 'tmax','prcp','wspd','wdir'])
        if len(df) ==0:
            df = pd.read_csv('weather.csv')
        fig = px.treemap(df, path=['variable'], values='value')
        fig.data[0].textinfo = 'label+value'
        

        level = 1 # write the number of the last level you have
        lvl_clr = "#5cb25d"
        font_clr = "black"

        fig.data[0]['marker']['colors'] =[lvl_clr for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]
        fig.data[0]['textfont']['color'] = [font_clr  for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]

        fig.data[0]['textfont']['size'] = 30

        return fig

# Generate a landcove background
def create_display(df, query=None):
    if query:
        # filter the dataframe to the selected point
        df = df.query(query)
        df = df.head(1)
        # df = pd.melt(df, value_vars=['tavg', 'tmin', 'tmax','prcp','wspd','wdir'])
        number = pn.indicators.Number(
            name='Avg Radiance', value=df['avg_radiance'], format='{value}%',
            colors=[(33, 'green'), (66, 'gold'), (100, 'red')]
        )
        fig=  pn.Row(
            number.clone(name='Deg Urban',value=df['avg_deg_urban']),
            # number.clone(name='Land Cover',value=df['land_cover_label']),
            # number.clone(name='Land Cover',value=df['land_cover_label'])
        )

        return fig

## function for creating the treemap to show specific point wise values 
def create_cards(df, query=None):
    if query:
        # filter the dataframe to the selected point
        df = df.query(query)
        df = pd.melt(df, value_vars=['tavg', 'tmin', 'tmax','prcp','wspd','wdir'])
        if len(df) ==0:
            df = pd.read_csv('weather.csv')
        fig = px.treemap(df, path=['variable'], values='value')
        fig.data[0].textinfo = 'label+value'
        

        level = 1 # write the number of the last level you have
        lvl_clr = "#5cb25d"
        font_clr = "black"

        fig.data[0]['marker']['colors'] =[lvl_clr for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]
        fig.data[0]['textfont']['color'] = [font_clr  for sector in fig.data[0]['ids'] if len(sector.split("/")) == level]

        fig.data[0]['textfont']['size'] = 30

        return fig

## function for creating the wordcloud to show specific point wise values 
def create_wordcloud(df, query=None):
    if query:
        # filter the dataframe to the selected point
        df = df.query(query)
        df = df.head(1)
        df = pd.melt(
            df.head(1),
            value_vars=[
                'land_cover_label',
                'snow',
                'is_invasive',
                'species',
                'country'])
        df['count']=[1,1,1,1,1]
        df['Title']= df['variable'].astype(str) +":" +df['value'].astype(str)

        df=df[['Title','count']]

        d = {a: x for a, x in df.values}
        wc = WordCloud(
            background_color='white',
            colormap='Set2',
            width=400,
            height=700)
        wc.fit_words(d)
        fig = wc.to_image()

        return fig

## function for creating the pie chart for soil
def create_pie(df, query=None):
    if query:
        ## filter the dataframe to the selected point
        df = df.query(query).copy()
        
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
            # color_discrete_sequence=px.colors.qualitative.Bold,
            color_discrete_sequence=px.colors.qualitative.Antique,
            # px.colors.sequential.Greens_r,
            hole=.3)
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        
        return fig


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
    # df=  df[df['country'] == 'Brazil']
    df_temp = df['species'].value_counts().rename_axis('Species').reset_index(name='Occurrence Count')
    df_temp = df_temp.sort_values(by = ['Occurrence Count'],ascending=[False])
    
    fig = px.bar(
        df_temp.head(10),
        x = 'Occurrence Count',
        y="Species",
        color="Species",
        color_discrete_sequence=
        # px.colors.cyclical.IceFire,
        px.colors.qualitative.Antique,
        text = 'Occurrence Count',
        title = 'Occurrence Counts for window <>'
    )
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

    return(fig)


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
plot_scatter = pn.pane.Plotly(occ_plot(species=species.value),width= 700, height= 550)
        
## dependent hidden function to run when a point is clicked in the plot_scatter
@pn.depends(plot_scatter.param.click_data, watch=True)
def _update_after_click_on_1(click_data):
    if click_data !=None:
        lat = click_data['points'][0]['lat']
        lon = click_data['points'][0]['lon']
        plot_pie.object = create_pie(df, f'decimalLatitude == {lat}')
        plot_cards.object = create_cards(df, f'decimalLatitude == {lat}')
        display_workcloud.object = create_wordcloud(df, f'decimalLatitude == {lat}')
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
        bq = query(start_date.value.strftime('%Y-%m-%d'), 
                   end_date.value.strftime('%Y-%m-%d'),
                   country.value) 
        if len(bq) > 0:
            df = bq.copy()
            plot_scatter.object = occ_plot(df, species.value)
            plot_cards.object = create_cards(df, f"decimalLatitude == {df.loc[0,'decimalLatitude']}")
            plot_pie.object = create_pie(df, f"decimalLatitude == {df.loc[0,'decimalLatitude']}")
            plot_trends.object = create_trends(df, f"decimalLatitude == {df.loc[0,'decimalLatitude']}")
            display_workcloud = create_wordcloud(df, f"decimalLatitude == {df.loc[0,'decimalLatitude']}")

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
plot_cards = pn.pane.Plotly(create_cards(df, f'decimalLatitude == -22.258903'), width=700, height=400)

###instantiate the pie plot
plot_pie = pn.pane.Plotly(create_pie(df, f'decimalLatitude == -22.258903'), width=700, height=450)

## display data, can delete later
cols = [ 'species','eventDate','decimalLatitude','decimalLongitude','country']
display_data = pn.widgets.DataFrame(df[cols].head(13),autosize_mode='fit_viewport')

## file download button
file_download_csv = pn.widgets.FileDownload(filename="gbif_covariates.csv", callback=get_csv, button_type="primary")

###what function to run when update buttton is pressed
button.on_click(fetch_data)

#instantiate display
display_stickers = create_display(df, f'decimalLatitude == -22.258903')


#instantiate wordcloud
display_workcloud =  pn.pane.PNG(create_wordcloud(df, f'decimalLatitude == -22.258903'))



############## The main template to render, sidebar for text

template = pn.template.FastGridTemplate(
    title="🌏 GBIF Powered by Covariates",
    header = ['<a href="https://github.com/tekritesh/bio-conservation/tree/main">About</a>'],
    sidebar=["""We are interested bleh bleh bleh.\n We will hunt you down if you harm ANY flora or fauna."""],
    accent = '#5cb25d',
    sidebar_width = 280,
    background_color = '#f5f5f5',
    neutral_color = '#ffffff',
    corner_radius = 15,
    modal = ["## No data for chosen filters. Please choose a different combination of parameters"]
)

############## specify which portion of the main page grid you want to place a plot in

template.main[:1, :] = pn.Row(pn.Column(start_date, end_date),
                              country,
                              species,
                              button)



template.main[1:5, 6:12]=pn.Tabs(('GBIF',pn.Column(plot_scatter)),
                              ('Radiance', pn.pane.HTML(HTML('map1.html'), width=600)), dynamic=True)

template.main[1:5,:6]= pn.Column('### Species Counts', plot_species, height=400)

number = pn.indicators.Number(
    name='Failure Rate', value=72, format='{value}',
    # color_discrete_sequence=px.colors.qualitative.Antique,
    colors=[(33, 'green'), (66, 'gold'), (100, 'red')]
)
template.main[5:6, :] = pn.Row(
    number.clone(name='Deg Urban',value=10,format='{value}%'),
    number.clone(name='Radiance',value=42,format='{value}%'),
    number.clone(name='Avg Temp',value=23,format='{value}C'),
    number.clone(name='WindSpeed',value=5,format='{value}mps'),
    number.clone(name='Precipitation',value=99)
    ) 
# template.main[5:6, :] = pn.Row(display_stickers)


template.main[6:9, :6] = pn.Column(plot_pie)

template.main[6:9, 6:12] = pn.Column(plot_cards)
# template.main[6:9, 6:12] = pn.Column(plot_trends)

template.main[9:13, :8]= pn.Column(file_download_csv, display_data, height=200, width = 200)

template.main[9:13, 8:12] = pn.Column(display_workcloud)


###color examples
##77cb
#'#faad55'
#'#f0a3bc'
#a18dd6


## tells the terminal command to run the template variable as a dashboard

template.servable();