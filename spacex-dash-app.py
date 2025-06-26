# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                            [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                # TASK 3: Add a slider to select payload range
                                html.Div([  # Added this Div wrapper for better structure
                                html.P("Payload range (Kg):", style={'margin-bottom': '10px'}),  # Added some margin
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={
                                        0: {'label': '0', 'style': {'color': '#77b0b1'}},
                                        2500: {'label': '2500', 'style': {'color': '#77b0b1'}},
                                        5000: {'label': '5000', 'style': {'color': '#77b0b1'}},
                                        7500: {'label': '7500', 'style': {'color': '#77b0b1'}},
                                        10000: {'label': '10000', 'style': {'color': '#77b0b1'}}
                                    },
                                    value=[min_payload, max_payload],
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                        "style": {"font-size": "12px"}  # Added font size for tooltip
                                    },
                                    pushable=500,  # Allows handles to push each other
                                    allowCross=False  # Prevents handles from crossing
                                )
                            ]),
                            html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # For all sites: show total successful launches per site
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='successes')
        fig = px.pie(success_counts, values='successes', names='Launch Site', title='Total Successful Launches by Site')
    else:
        # For specific site: show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        counts['class'] = counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, values='count', names='class', title=f'Success vs Failure for site {selected_site}')
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range selection
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                           (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Filter data based on launch site selection
    if selected_site == 'ALL':
        # Show data for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            labels={
                'Payload Mass (kg)': 'Payload Mass (kg)',
                'class': 'Launch Outcome'
            },
            hover_data=['Launch Site']
        )
    else:
        # Filter data for the selected site only
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {selected_site}',
            labels={
                'Payload Mass (kg)': 'Payload Mass (kg)',
                'class': 'Launch Outcome'
            }
        )
    
    # Customize the y-axis to show 0 and 1 with labels
    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=['Failure', 'Success']
    )
    
    # Improve layout
    fig.update_layout(
        xaxis_title='Payload Mass (kg)',
        yaxis_title='Launch Outcome',
        legend_title='Booster Version'
    )
    
    return fig
# Run the app
if __name__ == '__main__':
    app.run()
