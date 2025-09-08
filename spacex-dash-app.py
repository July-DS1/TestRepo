# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # For ALL sites: show total success launches by site (4 slices)
        # Calculate success count for each launch site
        success_by_site = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index()
        success_by_site.columns = ['Launch Site', 'Success Count']
        
        fig = px.pie(
            success_by_site, 
            values='Success Count', 
            names='Launch Site', 
            title='Total Success Launches by Site',
            color='Launch Site'
        )
    else:
        # For specific site: show success vs failure for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success', 'Failure'],
            title=f'Success vs Failure for {entered_site}',
            color=['Success', 'Failure'],
            color_discrete_map={'Success': 'green', 'Failure': 'red'}
        )
    
    # Update layout for better appearance
    fig.update_layout(
        title_x=0.5,  # Center title
        legend_title_text='Category'
    )
    
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # Further filter by site if a specific site is selected
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Launch Outcome',
        labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        hover_data=['Launch Site']
    )
    
    # Update y-axis to show proper labels
    fig.update_layout(
        title_x=0.5,
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success'])
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)