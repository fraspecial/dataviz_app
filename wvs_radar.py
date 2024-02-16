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

app = dash.Dash(__name__)


all_countries=list(sub['B_COUNTRY_ALPHA'].unique())
all_classes=list(sub['Q287P'].unique())
app.layout = html.Div([
    html.H1("Survey Results Comparison"),
    *[html.Div(children=[
        html.Div([
            html.Label('Dropdown 1'),
            dcc.Dropdown(
            id={'type':'dropdown', 'index':i},
            options=["All"]+all_countries,
            value=[all_countries[i]],
            multi=False,
        )], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Dropdown 2'),
            dcc.Dropdown(
                id={'type':'checklist', 'index':i},
                options=[
                {'label': 'Upper class', 'value': 1},
                {'label': 'Upper middle class', 'value': 2},
                {'label': 'Lower middle class', 'value': 3},
                {'label': 'Working class', 'value': 4},
                {'label': 'Lower class', 'value': 5},
                {'label': "Don't know", 'value': -1},
                {'label': "No answer", 'value': -.2},
                {'label': 'Not asked', 'value': -4},
                {'label': 'No answer; Missing', 'value': -5}
                ],
                multi=True,
                value=all_classes,
            #value=['check1'],
                )], style={'display': 'inline-block', 'margin-right': '20px'})]) for i in range(2)],
        dcc.Graph(id='spider-chart')]
)


@callback(
    Output({'type':"checklist", 'index':MATCH}, "value"),
    Output({'type':"all-checklist", 'index':MATCH}, "value"),
    Input({'type':"checklist", 'index':MATCH}, "value"),
    Input({'type':"all-checklist", 'index':MATCH}, "value"),
    prevent_initial_call=True
    )
def sync_checklists(cities_selected, all_selected):
    input_type = ctx.triggered_id.type

    if input_type=="checklist":
        all_selected = ["All"] if set(cities_selected) == set(all_classes) else []
    else:
        cities_selected = all_classes if all_selected else []
    return cities_selected, all_selected


# Define callback to update spider chart based on user input
@app.callback(
    Output('spider-chart', 'figure'),
    [Input({'type':'dropdown', 'index':ALL}, 'value'),
    Input({'type':'checklist', 'index':ALL}, 'value')]
)
def update_chart(countries, areas):
    #print(ctx.triggered_id)
    r_list=aggregate_info(sub, all_countries, all_classes, ["Q1P", "Q2P", "Q3P", "Q4P", "Q5P","Q6P"])
    r_list=np.append(r_list,r_list.iloc[0])
    fig=go.Figure(go.Scatterpolar(
            r=r_list,
            theta=["Family", "Friends", "Leisure time", "Work", "Politics", "Religion", "Family"],
            mode='text',
            fill = 'toself',
            name="All")
      )
    if ["All"] == countries[0]:
        countries[0]=all_countries
    for i in range(2):
        if not isinstance(countries[i],list):
            countries[i]=[countries[i]]
        r_list=aggregate_info(sub, countries[i], areas[i], ["Q1P", "Q2P", "Q3P", "Q4P", "Q5P","Q6P"])
        r_list=np.append(r_list,r_list.iloc[0])
    # Create spider chart with multiple traces for each country using Plotly Express

    #fig = go.Figure(go.Scatterpolar(r=starting_r_list, theta=theta_list, mode='text', name='mean', fill='toself'))

        fig.add_trace(go.Scatterpolar(
            r=r_list,
            theta=["Family", "Friends", "Leisure time", "Work", "Politics", "Religion", "Family"],
            mode='lines',
            fill = "none",
            name="All" if len(countries[i])==len(all_countries) else ' '.join(countries[i])
        ))

    # Set layout parameters
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,5])),
        showlegend=True,
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

# Create a Dash web application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.Div([
        html.Label('Dropdown 1'),
        dcc.Dropdown(
            id='dropdown1',
            options=[
                {'label': 'Option 1', 'value': 'opt1'},
                {'label': 'Option 2', 'value': 'opt2'},
                {'label': 'Option 3', 'value': 'opt3'}
            ],
            value='opt1'
        ),
    ], style={'display': 'inline-block', 'margin-right': '20px'}),

    html.Div([
        html.Label('Dropdown 2'),
        dcc.Dropdown(
            id='dropdown2',
            options=[
                {'label': 'Option A', 'value': 'optA'},
                {'label': 'Option B', 'value': 'optB'},
                {'label': 'Option C', 'value': 'optC'}
            ],
            value='optA'
        ),
    ], style={'display': 'inline-block'}),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
