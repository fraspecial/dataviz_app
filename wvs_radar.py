import dash
from dash import dcc, html, ctx, MATCH, ALL,callback
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def aggregate_info(sub, countries, classes, features):
    filtered_df = sub[(sub['B_COUNTRY_ALPHA'].isin(countries)) & (sub['Q287P'].isin(classes))].copy()
    r_list=(filtered_df[features].mul(filtered_df['W_WEIGHT'], axis='index')).sum()/(filtered_df['W_WEIGHT'].sum())
    return r_list

pd.DataFrame.iteritems=pd.DataFrame.items

url='"https://drive.google.com/file/d/1--sLuI8kkkTF9uYdEHO23VjM8D0C-_sC/view?usp=drive_link'
file_id=url.split('/')[-2]
dwn_url='https://drive.google.com/uc?id=' + file_id
sub=pd.read_csv(dwn_url, index_col=0)
sub[['Q1P', 'Q2P', 'Q3P', 'Q4P', 'Q5P', 'Q6P']]=sub[['Q1P', 'Q2P', 'Q3P', 'Q4P', 'Q5P', 'Q6P']]-1
sub.loc[sub['Q287P']<0, 'Q287P']=0
sub=sub.sort_values('B_COUNTRY_ALPHA')



all_countries=list(sub['B_COUNTRY_ALPHA'].unique())
all_classes=list(sub['Q287P'].unique())
app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'])
server=app.server
app.layout = html.Div([
    html.H1("What's important in life?"),
    html.P(['How much family, friends, work, politics, leisure time and religion matter from 0 ("Not at all important") to 3 ("Very important) for people all over the world?', html.Br(), 'Surprisingly ', html.B('it\'s not all about work at all!')]),
    html.Div(
        [html.Div([*[html.Div(children=[
            html.Div([
                html.Label(f'Group {i+1}',className='label'),
                dcc.Dropdown(
                id={'type':'dropdown', 'index':i},
                className='dropdown',
                options=['All']+all_countries,
                value=all_countries[i],
                multi=True,
                clearable=False
            )]),
            html.Div([
                html.Label('Select social class', className='label'),
                dcc.Checklist(
                    id={'type':'all-checklist', 'index':i},
                    options=[{'label': 'All', 'value':'All'}],
                    value=['All'],
                ),            
                dcc.Checklist(
                    id={'type':'checklist', 'index':i},
                    options=[
                    {'label': 'Upper class', 'value': 1},
                    {'label': 'Upper middle class', 'value': 2},
                    {'label': 'Lower middle class', 'value': 3},
                    {'label': 'Working class', 'value': 4},
                    {'label': 'Lower class', 'value': 5},
                    {'label': 'Unknown', 'value': 0}
                    ],
                    value=all_classes
                )], style={'margin-top':'12px'})], style={'display':'inline-block', 'width':'40%','margin-right':'20px'}) for i in range(2)],], style={'display': 'flex', "width":'50%'}),
            html.Div(dcc.Graph(id='spider-chart'), style={'width':'100%'})], id='container', style={'display':'flex', 'flex-direction':'row','margin-top':'25px'}),
            html.P('Source: ', style={'display':'inline', 'font-size': '10px', 'color':'#9e9e9e'}),html.a("World Value Survey Wave 7", href="https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp", style={'display': 'inline', 'color':'#e19899', 'font-size': '10px'})],
            style={'font-family':'Figtree'},
            )


@callback(
    Output({'type':"checklist", 'index':MATCH}, "value"),
    Output({'type':"all-checklist", 'index':MATCH}, "value"),
    Input({'type':"checklist", 'index':MATCH}, "value"),
    Input({'type':"all-checklist", 'index':MATCH}, "value"),
    prevent_initial_call=True
    )
def sync_checklists(classes_selected, all_selected):
    input_type = ctx.triggered_id.type

    if input_type=="checklist":
        all_selected = ["All"] if set(classes_selected) == set(all_classes) else []
    else:
        classes_selected = all_classes if all_selected else []
    return classes_selected, all_selected


# Define callback to update spider chart based on user input
@app.callback(
    Output('spider-chart', 'figure'),
    [Input({'type':'dropdown', 'index':ALL}, 'value'),
    Input({'type':'checklist', 'index':ALL}, 'value')],
)
def update_chart(countries, areas):
    r_list=aggregate_info(sub, all_countries, all_classes, ["Q1P", "Q2P", "Q3P", "Q4P", "Q5P","Q6P"])
    r_list=np.append(r_list,r_list.iloc[0])
    fig=go.Figure(go.Scatterpolar(
            r=r_list,
            theta=["Family", "Friends", "Leisure time", "Work", "Politics", "Religion", "Family"],
            mode='text',
            fill = 'toself',
            fillcolor='rgba(0,204,150,0.5)',
            hoveron='points',
            hovertemplate='%{theta}: %{r}<extra></extra>',
            name="All")
      )
    
    colors=['red', 'blue']
    for i in range(2):
        if not isinstance(countries[i],list):
            countries[i]=[countries[i]]
        if "All" in countries[i]:
            countries[i]=all_countries
        r_list=aggregate_info(sub, countries[i], areas[i], ["Q1P", "Q2P", "Q3P", "Q4P", "Q5P","Q6P"])
        r_list=np.append(r_list,r_list.iloc[0])
    # Create spider chart with multiple traces for each country using Plotly Express

    #fig = go.Figure(go.Scatterpolar(r=starting_r_list, theta=theta_list, mode='text', name='mean', fill='toself'))

        fig.add_trace(go.Scatterpolar(
            r=r_list,
            theta=["Family", "Friends", "Leisure time", "Work", "Politics", "Religion", "Family"],
            mode='lines',
            fill = "none",
            line={'color': colors[i]},
            hovertemplate='%{theta}: %{r}<extra></extra>',
            name=f'Group {i+1}'
        ))

    # Set layout parameters
    fig.update_layout(
        autosize=False,
        font=dict(family='Figtree', size=14),
        margin=dict(l=10,r=10,t=10,b=10),
        polar=dict(radialaxis=dict(visible=True, range=[0,3], gridcolor='grey'), angularaxis=dict(gridcolor='grey')),
        showlegend=True,
        plot_bgcolor='white',
        
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
