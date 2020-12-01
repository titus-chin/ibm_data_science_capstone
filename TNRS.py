# import necessary libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests

# initialize dash app
app=dash.Dash(__name__)
server=app.server

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
28 November 2020  
'''

md_map= '''
_Click on the map to change the neighborhood._
'''

# define function to visualize the score on a map
def create_map(result_df,ID=0,zoom=10,center={'lat':43.7047983,'lon':-79.3680904}):
    toronto_map=px.choropleth_mapbox(result_df,
                                     geojson=toronto_geojson,
                                     color='Score',
                                     locations='ID',
                                     color_continuous_scale='teal',
                                     featureidkey='properties.AREA_SHORT_CODE',
                                     mapbox_style='carto-positron',
                                     hover_data=['Rank','Neighborhood','Score'],
                                     zoom=zoom,
                                     center=center,
                                     opacity=0.7)
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
                                  center={'lat':43.7047983,'lon':-79.3680904},
                                  opacity=1)
    toronto_map.add_trace(fig_temp.data[0])
    hovertemplate='<br>Rank: %{customdata[0]}'\
                  '<br>%{customdata[1]}'\
                  '<br>Score: %{customdata[2]:.3s}%'\
                  '<extra></extra>'
    toronto_map.data[1]['hovertemplate']=hovertemplate  
    toronto_map.update_layout(margin={'r':0,'t':0,'l':0,'b':0},showlegend=False)
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
							 values='Percent')
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

# define function to get the score of each neighborhood
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
    result_df['Score']=(int(job_weightage)*temp_jobs+\
                        int(hai_weightage)*norm_affordability_df['HAI']+\
                        int(safety_weightage)*norm_crime_df['Crime Rate']+\
                        int(language_weightage)*temp_language+\
                        int(food_weightage)*temp_food)/\
                       (int(job_weightage)+int(hai_weightage)+int(safety_weightage)+int(language_weightage)+int(food_weightage))
    result_df['Score']=result_df['Score'].round(2)
    result_df.sort_values('Score',ascending=False,inplace=True)
    result_df.insert(loc=0,column='Rank',value=np.arange(1,141,1))
    result_df.reset_index(drop=True,inplace=True)
    return result_df

# set up initial data
result_df_initial=get_score(['Professional','Management'],['English','Mandarin'],['Fish & Chips Shop','Pizza Place'],4,5,4,4,3)

# set up app layout
app.layout = html.Div(className='app-body', children=[
    # stores
    dcc.Store(id='map_clicks', data=0),
    dcc.Store(id='ID',data=0),
    # title
    html.Div(className="row", children=[
        html.Div(className='twelve columns', children=[
            html.Div(style={'float': 'left'}, children=[
                    html.H1('Toronto\'s Neighborhoods Recommender System'),
                    html.H4('Out of 140 neighborhoods, choose the one suits you best!')
                ]
            ),
        ]),
    ]),
    # weightage
    html.Div(className="row", id='weightage', children=[
        html.Div(className="fix columns pretty_container", children=[
            html.Label('Jobs Weightage'),
            dcc.Slider(id='job_weightage',
                            value=4,
                            min=0, max=5, step=1,
                            marks={i: str(i) for i in range(0, 6, 1)}),
        ]),
        html.Div(className="fix columns pretty_container", children=[
            html.Label('Affordability Weightage'),
            dcc.Slider(id='hai_weightage',
                            value=5,
                            min=0, max=5, step=1,
                            marks={i: str(i) for i in range(0, 6, 1)}),
        ]),
        html.Div(className="fix columns pretty_container", children=[
            html.Label('Safety Weightage'),
            dcc.Slider(id='safety_weightage',
                            value=4,
                            min=0, max=5, step=1,
                            marks={i: str(i) for i in range(0, 6, 1)}),
        ]),
        html.Div(className="fix columns pretty_container", children=[
            html.Label('Language Weightage'),
            dcc.Slider(id='language_weightage',
                            value=4,
                            min=0, max=5, step=1,
                            marks={i: str(i) for i in range(0, 6, 1)}),
        ]),
        html.Div(className="fix columns pretty_container", children=[
            html.Label('Food Weightage'),
            dcc.Slider(id='food_weightage',
                            value=3,
                            min=0, max=5, step=1,
                            marks={i: str(i) for i in range(0, 6, 1)}),
        ]),
    ]),
    
       # filter
    html.Div(className="row", id='filter', children=[
        html.Div(className="four columns pretty_container", children=[
            html.Label('Select your favorite jobs'),
            dcc.Dropdown(id='jobs',
                         placeholder='Select jobs',
                         options=[{'label': job, 'value': job} for job in list(norm_jobs_df.columns[2:])],
                         value=['Professional','Management'],
                         multi=True),
        ]),
        html.Div(className="four columns pretty_container", children=[
            html.Label('Select your favorite languages'),
            dcc.Dropdown(id='language',
                         placeholder='Select languages',
                         options=[{'label': lan, 'value': lan} for lan in list(norm_language_df.columns[2:])],
                         value=['English','Mandarin'],
                         multi=True),
        ]),
        html.Div(className="four columns pretty_container", children=[
            html.Label('Select your favorite food'),
            dcc.Dropdown(id='food',
                         placeholder='Select food',
                         options=[{'label': f, 'value': f} for f in list(norm_food_df.columns[2:])],
                         value=['Fish & Chips Shop','Pizza Place'],
                         multi=True),
        ]),
    ]),

    # maps
    html.Div(className="row", children=[
    	html.Div(className="twelve columns pretty_container", children=[
    		dcc.Markdown(id='md_map', children=md_map),
    			dcc.Graph(id='toronto_map',
    			figure=create_map(result_df_initial),
    			config={"modeBarButtonsToRemove": ['lasso2d', 'select2d']})
                ]),
            ]),
            
     # sunburst and indicator
     html.Div(className="row", children=[
     	html.Div(className="fix columns pretty_container", children=[
     		dcc.Graph(id='sunburst_fig',
     		figure=create_sunburst(result_df_initial),
     		config={"modeBarButtonsToRemove": ['lasso2d', 'select2d']})
                ]),
        html.Div(className="fix columns pretty_container", children=[
        	dcc.Graph(id='indicator',
        	figure=create_indicator(result_df_initial),
        	config={"modeBarButtonsToRemove": ['lasso2d', 'select2d']})
                ]),
        ]),
        
    # about markdown
    html.Hr(),
    dcc.Markdown(children=about_md),
])

# map click call back
@app.callback(Output('ID','data'),
			  Input('toronto_map','clickData'),
			  State('ID','data'),
			  prevent_initial_call=True)
def click_action(click_data_toronto_map,ID):
	trg=dash.callback_context.triggered
	if trg is not None:
		component=trg[0]['prop_id'].split('.')[0]
		if component=='toronto_map':
			ID=trg[0]['value']['points'][0]['location']
	return ID

# toronto_map, sunburst_fig, indicator call back
@app.callback([Output('toronto_map','figure'),
			   Output('sunburst_fig','figure'),
			   Output('indicator','figure')],
			  [Input('jobs','value'),
			   Input('language','value'),
			   Input('food','value'),
			   Input('job_weightage','value'),
			   Input('hai_weightage','value'),
			   Input('safety_weightage','value'),
			   Input('language_weightage','value'),
			   Input('food_weightage','value'),
			   Input('ID','data')],
			  State('toronto_map','figure'),
			  prevent_initial_call=True)
def update_fig(jobs,language,food,job_weightage,hai_weightage,safety_weightage,language_weightage,food_weightage,ID,current_figure):
	trg=dash.callback_context.triggered
	if trg is not None:
		component=trg[0]['prop_id'].split('.')[0]
		if (component=='jobs')|(component=='language')|(component=='food')|(component=='job_weightage')|(component=='hai_weightage')|(component=='safety_weightage')|(component=='language_weightage')|(component=='food_weightage'):
			zoom=current_figure['layout']['mapbox']['zoom']
			center = current_figure['layout']['mapbox']['center']
			result_df=get_score(jobs,language,food,job_weightage,hai_weightage,safety_weightage,
			language_weightage,food_weightage)
			toronto_map=create_map(result_df,zoom=zoom,center=center)
			sunburst_fig=create_sunburst(result_df)
			indicator=create_indicator(result_df)
		else:
			zoom=current_figure['layout']['mapbox']['zoom']
			center = current_figure['layout']['mapbox']['center']
			result_df=get_score(jobs,language,food,job_weightage,hai_weightage,safety_weightage,
			language_weightage,food_weightage)
			toronto_map=create_map(result_df,ID,zoom=zoom,center=center)
			sunburst_fig=create_sunburst(result_df,ID)
			indicator=create_indicator(result_df,ID)
		return toronto_map,sunburst_fig,indicator	

if __name__ == '__main__':
    app.run_server(debug=True)	
