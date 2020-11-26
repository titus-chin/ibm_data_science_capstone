# import necessary libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input,Output,State
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
import geocoder
import logging
from flask_caching import Cache
import os

# initialize dash app
logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger('dash')
app=dash.Dash(__name__)
server=app.server
cache=Cache(app.server,config={'CACHE_TYPE':'filesystem','CACHE_DIR':'cache-directory'})
CACHE_TIMEOUT=int(os.environ.get('DASH_CACHE_TIMEOUT','60'))

# read all data required
percent_jobs_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/percent_jobs.csv')
top5_jobs_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/top5_jobs.csv')
norm_jobs_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/norm_jobs.csv')
affordability_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/affordability.csv')
norm_affordability_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/norm_affordability.csv')
crime_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/crime.csv')
norm_crime_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/norm_crime.csv')
percent_language_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/percent_language.csv')
top5_language_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/top5_language.csv')
norm_language_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/norm_language.csv')
percent_food_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/percent_food.csv')
top5_food_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/top5_food.csv')
norm_food_df=pd.read_csv('https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/norm_food.csv')
url='https://raw.githubusercontent.com/titus-chin/Toronto-Neighborhoods-Recommender-System/main/Data/boundary.geojson'
toronto_geojson=requests.get(url).json()
g=geocoder.osm('Leaside,Toronto,Ontario')
avg_crime=int(crime_df['Crime Rate'].mean())
avg_affordability=int(affordability_df['HAI'].mean())

# set layout/styling
fig_layout_defaults=dict(plot_bgcolor='#F9F9F9',paper_bgcolor='#F9F9F9')

# set markdown
about_md='''
### Toronto's Neighborhoods Recommender System

Read this [article]() to learn how to create such recommender system. Checkout the [GitHub repository](https://github.com/titus-chin/Toronto-Neighborhoods-Recommender-System) for the source code.

Created by:  
[Titus Chin Jun Hong](https://www.linkedin.com/in/titus-chin-a17ba41bb/)  
26 November 2020  
'''

# define function to style the table
def data_bars(df,column):
	n_bins=100
    bounds=[i*(1.0/n_bins)for i in range(n_bins+1)]
    ranges=[((df[column].max()-df[column].min())*i)+df[column].min()for i in bounds]
    styles=[]
    for i in range(1,len(bounds)):
    	min_bound=ranges[i-1]
    	max_bound=ranges[i]
        max_bound_percentage=bounds[i]*100
        styles.append({
            'if':{
                'filter_query':(
                    '{{{column}}}>={min_bound}'+
                    ('&&{{{column}}}<{max_bound}'if(i<len(bounds)-1)else'')
                ).format(column=column,min_bound=min_bound,max_bound=max_bound),
                'column_id':column
            },
            'background':(
                """
                    linear-gradient(90deg,
                    #00c1c1 0%,
                    #00c1c1 {max_bound_percentage}%,
                    #F9F9F9 {max_bound_percentage}%,
                    #F9F9F9 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom':2,
            'paddingTop':2
        })
    return styles

# define function to visualize the score on a map
def create_map(result_df,ID=0):
    toronto_map=px.choropleth_mapbox(result_df,
                                     geojson=toronto_geojson,
                                     color='Score',
                                     color_continuous_scale='teal',
                                     locations='ID',
                                     featureidkey='properties.AREA_SHORT_CODE',
                                     mapbox_style='carto-positron',
                                     hover_data=['Rank','Neighborhood','Score'],
                                     zoom=10,
                                     center={'lat':g.latlng[0],'lon':g.latlng[1]},
                                     opacity=0.5)
    hovertemplate='<br>Rank: %{customdata[0]}'\
                  '<br>%{customdata[1]}'\
                  '<br>Score: %{customdata[2]:.3s}%'
    toronto_map.data[0]['hovertemplate']=hovertemplate

    # draw selected ID
    selected_geojson=toronto_geojson.copy()
    if ID==0:
        selected_df=result_df[result_df['Rank']==1]
    else:
        selected_df=result_df[result_df['ID']==ID]
    for feature in selected_geojson['features']:
        if feature['properties']['AREA_SHORT_CODE']==selected_df.iloc[0,2]:
            selected_geojson['features']=[feature]
    data_selected={'ID':selected_df.iloc[0,2],
                   'Neighborhood':selected_df.iloc[0,1],
                   'default_value':[''],
                   'Rank':selected_df.iloc[0,0],
                   'Score':selected_df.iloc[0,3]}
    fig_temp=px.choropleth_mapbox(data_selected,
                                  geojson=selected_geojson,
                                  locations='ID',
                                  color='default_value',
                                  featureidkey='properties.AREA_SHORT_CODE',
                                  mapbox_style="carto-positron",
                                  hover_data=['Rank','Neighborhood','Score'],
                                  zoom=10,
                                  center={'lat':g.latlng[0],'lon':g.latlng[1]},
                                  opacity=1)
    toronto_map.add_trace(fig_temp.data[0])
    hovertemplate='<br>Rank: %{customdata[0]}'\
                  '<br>%{customdata[1]}'\
                  '<br>Score: %{customdata[2]:.3s}%'\
                  '<extra></extra>'
    toronto_map.data[1]['hovertemplate']=hovertemplate  
    toronto_map.update_layout(margin={'r':0,'t':0,'l':0,'b':0},coloraxis_showscale=False,showlegend=False)
    return toronto_map

# define function to visualize the top5 jobs, languages and food of selected neighborhood on sunburst figure
def create_sunburst(result_df,ID=0):
	if ID==0:
        i=(result_df['ID'][0])-1
    else:
        i=ID-1
	top5=list(top5_jobs_df.iloc[i,2:].values)+list(top5_language_df.iloc[i,2:].values)+\
		 list(top5_food_df.iloc[i,2:].values)
	temp_jobs=list(percent_jobs_df.iloc[i,2:].values)
	temp_jobs.sort(reverse=True)
	temp_language=list(percent_language_df.iloc[i,2:].values)
	temp_language.sort(reverse=True)
	temp_food=list(percent_food_df.iloc[i,2:].values)
	temp_food.sort(reverse=True)
	percent=temp_jobs[0:5]+temp_language[0:5]+temp_food[0:5]
	factor=['Jobs','Jobs','Jobs','Jobs','Jobs','Languages','Languages','Languages','Languages','Languages','Food',
		   'Food','Food','Food','Food']
	result_df=pd.DataFrame({'Factor':factor,'Top5':top5,'Percent':percent})
	sunburst_fig=px.sunburst(result_df,
							 path=['Factor','Top5'],
							 values='Percent',
							 color='Percent',
							 color_continuous_scale='teal')
	hovertemplate='<br>%{label}'\
		          '<br>%{value:.3s}%'
	sunburst_fig.data[0]['hovertemplate']=hovertemplate
	sunburst_fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0},coloraxis_showscale=False,showlegend=False,**fig_layout_defaults)
	return sunburst_fig

# define function to visualize the crime rate and affordability index of selected neighborhood on indicator
def create_indicator(result_df,ID=0):
	if ID==0:
        i=(result_df['ID'][0])-1
    else:
        i=ID-1
	indicator=go.Figure()
	indicator.add_trace(go.Indicator(mode='number+delta',
		                             value=crime_df.iloc[i,2],
		                             title={'text':'Crime Rate'},
		                             delta={'reference':avg_crime,'relative':True,'increasing_color':'#FF4136',
		                                    'decreasing_color':'#3D9970'},
		                             domain={'x':[0,1],'y':[0,0.5]}))
	indicator.add_trace(go.Indicator(mode='number+delta',
		                             value=affordability_df.iloc[i,2],
		                             title={'text':'Affordability Index'},
		                             delta={'reference':avg_affordability,'relative':True},
		                             domain={'x':[0,1],'y':[0.4,1]}))
	indicator.update_layout(margin={'r':0,'t':0,'l':0,'b':0},**fig_layout_defaults)
	return indicator

# define function to create a table consisting of rank, neighborhood and score




# define a function to get the score of each neighborhood based on our choices
def get_score(jobs,language,food,job_weightage,hai_weightage,safety_weightage,language_weightage,food_weightage):
    result_df=norm_jobs_df.iloc[:,0:2]
    temp_jobs=0
    for job in jobs:
        temp_jobs=temp_jobs+norm_jobs_df[job]
    if len(jobs)>0:
        temp_jobs=temp_jobs/len(jobs)   
    temp_language=0
    for lan in language:
        temp_language=temp_language+norm_language_df[lan]
    if len(language)>0:
        temp_language=temp_language/len(language)
    temp_food=0
    for f in food:
        temp_food=temp_food+norm_food_df[f]
    if len(food)>0:
        temp_food=temp_food/len(food)        
    result_df['Score']=(job_weightage*temp_jobs+\
                        hai_weightage*norm_affordability_df['HAI']+\
                        safety_weightage*norm_crime_df['Crime Rate']+\
                        language_weightage*temp_language+\
                        food_weightage*temp_food)/\
                       (job_weightage+hai_weightage+safety_weightage+language_weightage+food_weightage)
    result_df['Score']=result_df['Score'].round(2)
    result_df.sort_values('Score',ascending=False,inplace=True)
    result_df.insert(loc=0,column='Rank',value=np.arange(1,141,1))
    result_df.reset_index(drop=True,inplace=True)
    return display(result_df)







 

 
    
    
    
    # set up widgets to filter the results
item=[widgets.SelectMultiple(options=list(norm_jobs_df.columns[2:]),description='Jobs',
                             value=('Professional','Management')),
      widgets.SelectMultiple(options=list(norm_language_df.columns[2:]),description='Language',
                             value=('English','Mandarin')),
      widgets.SelectMultiple(options=list(norm_food_df.columns[2:]),description='Food',
                             value=('Fish & Chips Shop','Pizza Place')),
      widgets.IntSlider(min=0,max=5,value=4,step=1,description='Job Weightage',continuous_update=False),
      widgets.IntSlider(min=0,max=5,value=5,step=1,description='Affordability Weightage',continuous_update=False),
      widgets.IntSlider(min=0,max=5,value=4,step=1,description='Safety Weightage',continuous_update=False),
      widgets.IntSlider(min=0,max=5,value=4,step=1,description='Language Weightage',continuous_update=False),
      widgets.IntSlider(min=0,max=5,value=3,step=1,description='Food Weightage',continuous_update=False)]
