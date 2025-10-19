# %%
# app.py - Main Dashboard Application
import dash
from dash import dcc, html, Input, Output, callback
import traceback
import plotly.graph_objects as go
import sys
sys.path.append(r"H:\My Drive\nci_data_viz\project_file\production")
# Try to import custom modules with error handling
import dash_bootstrap_components as dbc
import dataloader
import gen_graph
import base64
import os
import pandas as pd


# %%
#load data
asr1=dataloader.load_thai_asr_data()
asr2= dataloader.load_thai_asr_age_data()
asr3=dataloader.load_region_data()
surv= dataloader.load_survival_data()
prov_hr=dataloader.load_prov_data()

#load filter options
fig1_option = dataloader.get_dropdown_options(asr1)
fig1_option.pop('years', None)

fig2_option = dataloader.get_dropdown_options(asr2)
fig2_option.pop('years', None)
fig2_option.pop('age_groups', None)
fig2_option.pop('sex_options', None)

fig3_option = dataloader.get_dropdown_options(asr1)
fig3_option.pop('sex_options', None)
fig3_option.pop('cancer_types', None)

fig4_option = dataloader.get_dropdown_options(asr3)
fig4_option.pop('health_regions', None)

fig5_option = dataloader.get_dropdown_options2(surv)

# %%
def encode_image(image_path):
    """Convert image to base64 string for embedding in Dash"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""

image_folder = r"H:\My Drive\nci_data_viz\project_file\image"
image1_path = image_folder + r"\Screenshot 2025-09-30 143934.png"
image2_path = image_folder + r"\Screenshot 2025-09-30 144008.png"

# Encode images
image1_base64 = encode_image(image1_path)
image2_base64 = encode_image(image2_path)

# %%
# Initialize Dash app with Bootstrap theme (reinitialize to ensure fresh instance)
try:
    if 'app' in globals():
        del app
except:
    pass

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.COSMO,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
])
app.title = "Thailand Cancer Data Visualization"

# Expose the server for deployment platforms like Render
server = app.server

# Define the layout for the uppermost part with responsive images
app.layout = dbc.Container([
    # Header section with images and title
    dbc.Row([
        # Left column for image1
        dbc.Col([
            html.Img(
                src=image1_base64,
                style={
                    'width': '80%',
                    'height': 'auto',
                    'max-height': '150px',
                    'max-width': '200px',
                    'object-fit': 'contain',
                    'border-radius': '8px',
                    'box-shadow': '0 4px 8px rgba(0,0,0,0.1)',
                    'margin': '0',
                    'display': 'block'
                },
                className="img-fluid"
            )
        ], 
        xs=12, sm=12, md=3, lg=3, xl=3,
        className="mb-3 mb-md-0 text-center"
        ),
        
        # Center column for title
        dbc.Col([
            html.Div([
                html.H3("Thailand Cancer Incidence Data Visualization Dashboard", 
                       className="text-center mb-2",
                       style={
                           'font-weight': 'bold',
                           'color': "#071625",
                           'font-size': '2.2rem'
                       }),
                html.P("National Cancer Institute - Statistical Analysis and Reporting System V1.0", 
                      className="text-center text-muted mb-0",
                      style={'font-size': '1rem'})
            ])
        ], 
        xs=12, sm=12, md=6, lg=6, xl=6,
        className="mb-3 mb-md-0 d-flex align-items-center justify-content-center"
        ),
        
        # Right column for image2
        dbc.Col([
            html.Img(
                src=image2_base64,
                style={
                    'width': '100%',
                    'height': 'auto',
                    'max-height': '250px',
                    'max-width': '300px',
                    'object-fit': 'contain',
                    'border-radius': '8px',
                    'box-shadow': '0 4px 8px rgba(0,0,0,0.1)',
                    'margin': '0 0 0 auto',
                    'display': 'block'
                },
                className="img-fluid"
            )
        ], 
        xs=12, sm=12, md=3, lg=3, xl=3,
        className="mb-3",
        style={'text-align': 'right'} 
        )
    ], 
    className="g-3",
    justify="center",
    align="center"
    ),
    
    # Long horizontal bar across the page under images
    dbc.Row([
        dbc.Col([
            html.Div(
                style={
                    'width': '100%',
                    'height': '4px',
                    'background': 'linear-gradient(90deg, #007bff, #0056b3)',
                    'margin': '20px 0',
                    'border-radius': '2px',
                    'box-shadow': '0 2px 4px rgba(0,123,255,0.2)'
                }
            )
        ], width=12)
    ], className="mb-3"),
    
    # Horizontal Visualization Selection Buttons at top
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Select Visualization", 
                       className="text-center mb-3",
                       style={
                           'color': '#005eaa',
                           'font-weight': '600',
                           'border-bottom': '3px solid #005eaa',
                           'padding-bottom': '10px'
                       }),
                
                # 6 Beautiful Horizontal Selection Buttons
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.Div([
                                html.I(className="fas fa-chart-line", style={'font-size': '1.5rem', 'color': '#007bff'}),
                                html.Br(),
                                html.Span("Cancer Trends", style={'font-size': '0.9rem', 'font-weight': '600'})
                            ])
                        ],
                            id="btn-trend",
                            color="light",
                            className="w-100 shadow-sm",
                            style={
                                'height': '85px',
                                'border': '2px solid #007bff',
                                'border-radius': '12px',
                                'background': 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                                'transition': 'all 0.3s ease',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            }
                        )
                    ], xs=12, sm=6, md=4, lg=2, xl=2),
                    dbc.Col([
                        dbc.Button([
                            html.Div([
                                html.I(className="fas fa-users", style={'font-size': '1.5rem', 'color': '#28a745'}),
                                html.Br(),
                                html.Span("Age Distribution", style={'font-size': '0.9rem', 'font-weight': '600'})
                            ])
                        ],
                            id="btn-age",
                            color="light",
                            className="w-100 shadow-sm",
                            style={
                                'height': '85px',
                                'border': '2px solid #28a745',
                                'border-radius': '12px',
                                'background': 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                                'transition': 'all 0.3s ease',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            }
                        )
                    ], xs=12, sm=6, md=4, lg=2, xl=2),
                    dbc.Col([
                        dbc.Button([
                            html.Div([
                                html.I(className="fas fa-trophy", style={'font-size': '1.5rem', 'color': '#ffc107'}),
                                html.Br(),
                                html.Span("Top 10 Cancers", style={'font-size': '0.9rem', 'font-weight': '600'})
                            ])
                        ],
                            id="btn-top10",
                            color="light",
                            className="w-100 shadow-sm",
                            style={
                                'height': '85px',
                                'border': '2px solid #ffc107',
                                'border-radius': '12px',
                                'background': 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                                'transition': 'all 0.3s ease',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            }
                        )
                    ], xs=12, sm=6, md=4, lg=2, xl=2),
                    dbc.Col([
                        dbc.Button([
                            html.Div([
                                html.I(className="fas fa-map-marked-alt", style={'font-size': '1.5rem', 'color': '#17a2b8'}),
                                html.Br(),
                                html.Span("Health Regions", style={'font-size': '0.9rem', 'font-weight': '600'})
                            ])
                        ],
                            id="btn-map",
                            color="light",
                            className="w-100 shadow-sm",
                            style={
                                'height': '85px',
                                'border': '2px solid #17a2b8',
                                'border-radius': '12px',
                                'background': 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                                'transition': 'all 0.3s ease',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            }
                        )
                    ], xs=12, sm=6, md=4, lg=2, xl=2),
                    dbc.Col([
                        dbc.Button([
                            html.Div([
                                html.I(className="fas fa-heart-pulse", style={'font-size': '1.5rem', 'color': '#dc3545'}),
                                html.Br(),
                                html.Span("Survival", style={'font-size': '0.9rem', 'font-weight': '600'})
                            ])
                        ],
                            id="btn-stats",
                            color="light",
                            className="w-100 shadow-sm",
                            style={
                                'height': '85px',
                                'border': '2px solid #dc3545',
                                'border-radius': '12px',
                                'background': 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                                'transition': 'all 0.3s ease',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            }
                        )
                    ], xs=12, sm=6, md=4, lg=2, xl=2),
                    dbc.Col([
                        dbc.Button([
                            html.Div([
                                html.I(className="fas fa-skull", style={'font-size': '1.5rem', 'color': '#6f42c1'}),
                                html.Br(),
                                html.Span("Mortality", style={'font-size': '0.9rem', 'font-weight': '600'})
                            ])
                        ],
                            id="btn-table",
                            color="light",
                            className="w-100 shadow-sm",
                            style={
                                'height': '85px',
                                'border': '2px solid #6f42c1',
                                'border-radius': '12px',
                                'background': 'linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)',
                                'transition': 'all 0.3s ease',
                                'display': 'flex',
                                'align-items': 'center',
                                'justify-content': 'center'
                            }
                        )
                    ], xs=12, sm=6, md=4, lg=2, xl=2)
                ], className="g-3")
            ], 
            style={
                'background': 'linear-gradient(145deg, #e7f2f8 0%, #d4e9f7 100%)',
                'padding': '2rem',
                'border-radius': '8px',
                'border': '1px solid #b3d9f2',
                'box-shadow': '0 2px 8px rgba(0,94,170,0.1)'
            })
        ], width=12)
    ], className="mb-4"),
    
    # Main Visualization Section: Sidebar (20%) + Content (80%)
    dbc.Row([
        # Left Sidebar - 20% width with Filters
        dbc.Col([
            html.Div([
                # Filter Section
                html.H6("Filters", 
                       className="text-center mb-3",
                       style={
                           'color': '#005eaa',
                           'font-weight': '600',
                           'font-size': '1rem',
                           'border-bottom': '2px solid #005eaa',
                           'padding-bottom': '8px'
                       }),
                
                # Filter 1 - Year
                html.Div(id='year-filter-container', children=[
                    html.Label("Year:", 
                              style={
                                  'font-weight': '600',
                                  'font-size': '1rem',
                                  'color': '#333',
                                  'margin-bottom': '8px',
                                  'display': 'block'
                              }),
                    dcc.Dropdown(
                        id='filter-year',
                        options=[
                            {'label': 'All Years', 'value': 'all'},
                            {'label': '2020', 'value': 2020},
                            {'label': '2019', 'value': 2019},
                            {'label': '2018', 'value': 2018}
                        ],
                        value='all',
                        clearable=False,
                        style={
                            'fontSize': '16px',
                            'minHeight': '50px'
                        },
                        className='custom-dropdown',
                        optionHeight=48
                    )
                ], className="mb-3"),
                
                # Filter 2 - Cancer Site
                html.Div(id='site-filter-container', children=[
                    html.Label("Cancer Site:", 
                              style={
                                  'font-weight': '600',
                                  'font-size': '1rem',
                                  'color': '#333',
                                  'margin-bottom': '8px',
                                  'display': 'block'
                              }),
                    dcc.Dropdown(
                        id='filter-site',
                        options=[
                            {
                                'label': cancer_type if len(cancer_type) <= 25 else cancer_type[:22] + '...',
                                'value': cancer_type,
                                'title': cancer_type  # Full name on hover
                            } 
                            for cancer_type in fig1_option.get('cancer_types', [])
                        ],
                        value='Breast',
                        clearable=False,
                        style={
                            'fontSize': '16px',
                            'minHeight': '50px'
                        },
                        className='custom-dropdown',
                        optionHeight=48,
                        maxHeight=280
                    )
                ], className="mb-3"),
                
                # Filter 3 - Sex
                html.Div(id='sex-filter-container', children=[
                    html.Label("Sex:", 
                              style={
                                  'font-weight': '600',
                                  'font-size': '1rem',
                                  'color': '#333',
                                  'margin-bottom': '8px',
                                  'display': 'block'
                              }),
                    dcc.Dropdown(
                        id='filter-sex',
                        options=[{'label': 'Both Sexes', 'value': 'Both'}] + [{'label': sex_opt, 'value': sex_opt} for sex_opt in fig1_option.get('sex_options', [])],
                        value='Both',
                        clearable=False,
                        style={
                            'fontSize': '15px',
                            'minHeight': '44px'
                        },
                        className='custom-dropdown',
                        optionHeight=42
                    )
                ], className="mb-3"),
                
                # Filter 4 - Health Regions (for survival data)
                html.Div(id='region-filter-container', children=[
                    html.Label("Health Regions:", 
                              style={
                                  'font-weight': '600',
                                  'font-size': '1rem',
                                  'color': '#333',
                                  'margin-bottom': '8px',
                                  'display': 'block'
                              }),
                    dcc.Dropdown(
                        id='filter-region',
                        options=[{'label': f'Region {region}', 'value': region} for region in fig5_option.get('health_regions', [])] + [{'label': 'All Regions', 'value': 'all'}],
                        value=['all', '2'],
                        multi=True,
                        clearable=False,
                        placeholder="Select up to 3 regions",
                        style={
                            'fontSize': '15px',
                            'minHeight': '44px'
                        },
                        className='custom-dropdown',
                        optionHeight=42
                    )
                ], className="mb-3"),
                
                # Filter 5 - Cancer Stages (for survival data)
                html.Div(id='stage-filter-container', children=[
                    html.Label("Cancer Stages:", 
                              style={
                                  'font-weight': '600',
                                  'font-size': '1rem',
                                  'color': '#333',
                                  'margin-bottom': '8px',
                                  'display': 'block'
                              }),
                    dcc.Dropdown(
                        id='filter-stage',
                        options=[{'label': stage.title(), 'value': stage} for stage in fig5_option.get('stages', [])],
                        value=['stage1', 'stage2', 'stage3', 'stage4'],
                        multi=True,
                        clearable=False,
                        placeholder="Select up to 4 stages",
                        style={
                            'fontSize': '15px',
                            'minHeight': '44px'
                        },
                        className='custom-dropdown',
                        optionHeight=42
                    )
                ], className="mb-3"),
                
                # Apply Button
                html.Div([
                    dbc.Button(
                        "Apply Filters",
                        id="btn-apply-filters",
                        color="success",
                        className="w-100",
                        style={
                            'font-weight': '600',
                            'font-size': '0.95rem',
                            'padding': '12px',
                            'margin-top': '10px'
                        }
                    )
                ], className="mb-3")
                
            ], 
            style={
                'background': 'linear-gradient(145deg, #e7f2f8 0%, #d4e9f7 100%)',
                'padding': '1.5rem',
                'border-radius': '8px',
                'border': '1px solid #b3d9f2',
                'box-shadow': '0 2px 8px rgba(0,94,170,0.1)',
                'height': '100%',
                'min-height': '500px'
            })
        ], xs=12, sm=12, md=3, lg=3, xl=3, className="mb-3 mb-md-0"),
        
        # Right Content Area - Adjusted width for slightly wider filter column
        dbc.Col([
            html.Div([
                html.H5("Visualization Area", 
                       className="text-center mb-3",
                       style={
                           'color': '#005eaa',
                           'font-weight': '600'
                       }),
                html.Div(
                    id='content-area',
                    children=[
                        html.P("Select a visualization from the buttons above to display content here.",
                              className="text-center text-muted",
                              style={'padding': '3rem', 'font-size': '1.1rem'})
                    ],
                    style={'min-height': '400px'}
                )
            ], 
            style={
                'background': '#ffffff',
                'padding': '2rem',
                'border-radius': '8px',
                'border': '1px solid #dee2e6',
                'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                'height': '100%',
                'min-height': '500px'
            })
        ], xs=12, sm=12, md=9, lg=9, xl=9)
    ], className="mb-4"),
    
    # Visualization Description Section - Below the visualization area
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Visualization Description", 
                       className="text-center mb-3",
                       style={
                           'color': '#005eaa',
                           'font-weight': '600'
                       }),
                html.Div(
                    id='figure-description',
                    children=[
                        html.Div([
                            html.H6("📊 Cancer Trends", 
                                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
                            html.P([
                                "Displays temporal trends of cancer incidence rates over multiple years. ",
                                "This visualization helps identify patterns, increasing or decreasing trends, ",
                                "and potential emerging concerns in cancer epidemiology."
                            ], style={'line-height': '1.6', 'color': '#333'}),
                            html.Hr(style={'margin': '20px 0'}),
                            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
                            html.Ul([
                                html.Li("Interactive line charts showing year-over-year changes"),
                                html.Li("Age-standardized rates (ASR) per 100,000 population"),
                                html.Li("Comparison across different cancer sites"),
                                html.Li("Statistical trend analysis and projections")
                            ], style={'line-height': '1.8', 'color': '#555'})
                        ], style={'padding': '20px'})
                    ],
                    style={'min-height': '250px'}
                )
            ], 
            style={
                'background': '#ffffff',
                'padding': '2rem',
                'border-radius': '8px',
                'border': '1px solid #dee2e6',
                'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                'height': '100%',
                'min-height': '300px'
            })
        ], xs=12, sm=12, md=12, lg=12, xl=12, className="mb-3")
    ], className="mb-4")
    
], fluid=True, className="px-3 py-4")


# %%
# Add custom CSS for better mobile responsiveness
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Beautiful button styles */
            .btn:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
                border-width: 3px !important;
            }
            
            .btn:active {
                transform: translateY(0px) !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
            }
            
            .btn.active, .btn:focus {
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
                border-width: 3px !important;
            }
            
            /* Button icon and text styling */
            .btn i {
                margin-bottom: 5px !important;
                transition: all 0.3s ease !important;
            }
            
            .btn:hover i {
                transform: scale(1.1) !important;
            }
            
            /* Dropdown styling to prevent text overlap - Updated for newer Dash */
            .dash-dropdown .dropdown {
                font-size: 0.9rem !important;
            }
            
            /* Fix grey artifacts in newer Dash versions */
            .dash-dropdown .dropdown__single-value {
                background-color: transparent !important;
                color: #333 !important;
            }
            
            .dash-dropdown .dropdown__placeholder {
                background-color: transparent !important;
                color: #666 !important;
            }
            
            .dash-dropdown .dropdown__control {
                background-color: #ffffff !important;
                border: 1px solid #ced4da !important;
            }
            
            /* Dropdown indicators positioning */
            .dash-dropdown .dropdown__indicators {
                position: absolute !important;
                right: 8px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
            
            .dash-dropdown .dropdown__indicator {
                padding: 4px !important;
                color: #666 !important;
            }
            
            .dash-dropdown .Select-control,
            .dash-dropdown .dropdown__control {
                min-height: 40px !important;
                border: 1px solid #ced4da !important;
                border-radius: 6px !important;
                box-shadow: none !important;
                position: relative !important;
            }
            
            .dash-dropdown .Select-value-label,
            .dash-dropdown .dropdown__single-value,
            .dash-dropdown .dropdown__placeholder {
                line-height: 1.5 !important;
                padding: 8px 35px 8px 12px !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                font-size: 0.9rem !important;
            }
            
            .dash-dropdown .Select-option,
            .dash-dropdown .dropdown__option {
                padding: 8px 12px !important;
                line-height: 1.5 !important;
                white-space: normal !important;
                word-wrap: break-word !important;
                min-height: 36px !important;
                font-size: 0.9rem !important;
                display: flex !important;
                align-items: center !important;
            }
            
            .dash-dropdown .Select-menu-outer,
            .dash-dropdown .dropdown__menu {
                max-height: 250px !important;
                z-index: 9999 !important;
                border: 1px solid #ced4da !important;
                border-radius: 6px !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
            }
            
            .dash-dropdown .Select-control:hover,
            .dash-dropdown .dropdown__control:hover {
                border-color: #007bff !important;
            }
            
            .dash-dropdown .is-focused .Select-control,
            .dash-dropdown .dropdown__control--is-focused {
                border-color: #007bff !important;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25) !important;
            }
            
            .dash-dropdown .Select-input,
            .dash-dropdown .dropdown__input {
                height: auto !important;
                padding: 0 !important;
            }
            
            /* Multi-select specific styling */
            .dash-dropdown .Select-multi-value-wrapper,
            .dash-dropdown .dropdown__multi-value__generic {
                padding: 2px 8px !important;
            }
            
            .dash-dropdown .Select-value,
            .dash-dropdown .dropdown__multi-value {
                margin: 2px !important;
                background-color: #e9ecef !important;
                border-radius: 4px !important;
            }
            
            /* Custom dropdown class for better text handling */
            .custom-dropdown .Select-control {
                min-height: 52px !important;
                padding: 4px 8px !important;
                display: flex !important;
                align-items: center !important;
                background-color: #ffffff !important;
                border: 1px solid #ced4da !important;
                border-radius: 6px !important;
                position: relative !important;
            }
            
            .custom-dropdown .Select-input {
                padding-right: 35px !important;
            }
            
            .custom-dropdown .Select-value-label {
                padding: 12px 8px !important;
                padding-right: 40px !important;
                line-height: 1.4 !important;
                max-width: calc(100% - 50px) !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                white-space: nowrap !important;
                font-size: 16px !important;
                display: block !important;
                background-color: transparent !important;
                color: #333 !important;
            }
            
            .custom-dropdown .Select-placeholder {
                padding: 8px 6px !important;
                padding-right: 35px !important;
                line-height: 1.4 !important;
                font-size: 15px !important;
                background-color: transparent !important;
                color: #666 !important;
            }
            
            .custom-dropdown .Select-option {
                padding: 10px 12px !important;
                line-height: 1.4 !important;
                min-height: 44px !important;
                display: flex !important;
                align-items: center !important;
                white-space: normal !important;
                word-break: break-word !important;
                overflow-wrap: break-word !important;
                font-size: 15px !important;
            }
            
            .custom-dropdown .Select-menu {
                max-height: 280px !important;
                overflow-y: auto !important;
                border: 1px solid #ced4da !important;
                border-radius: 6px !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            }
            
            .custom-dropdown .Select-input {
                height: auto !important;
                padding: 0 !important;
                background-color: transparent !important;
            }
            
            .custom-dropdown .Select-arrow-zone {
                padding: 8px 12px !important;
                position: absolute !important;
                right: 0 !important;
                top: 0 !important;
                bottom: 0 !important;
                display: flex !important;
                align-items: center !important;
                pointer-events: none !important;
                width: 35px !important;
            }
            
            .custom-dropdown .Select-arrow {
                border-color: #666 transparent transparent !important;
                border-style: solid !important;
                border-width: 5px 5px 0 !important;
                display: inline-block !important;
                height: 0 !important;
                width: 0 !important;
            }
            
            /* Fix for grey artifacts and text selection issues */
            .custom-dropdown .Select-value {
                background-color: transparent !important;
                color: #333 !important;
            }
            
            .custom-dropdown .Select-control:focus {
                outline: none !important;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25) !important;
            }
            
            .custom-dropdown .Select-control .Select-value-label::-moz-selection {
                background-color: transparent !important;
            }
            
            .custom-dropdown .Select-control .Select-value-label::selection {
                background-color: transparent !important;
            }
            
            /* Remove any default browser selection styling */
            .custom-dropdown * {
                -webkit-user-select: none !important;
                -moz-user-select: none !important;
                -ms-user-select: none !important;
                user-select: none !important;
            }
            
            /* Mobile-first responsive CSS */
            @media (max-width: 768px) {
                .container-fluid {
                    padding-left: 10px !important;
                    padding-right: 10px !important;
                }
                
                /* Make buttons stack on mobile and adjust size */
                .btn {
                    margin-bottom: 8px !important;
                    height: 70px !important;
                }
                
                .btn i {
                    font-size: 1.2rem !important;
                }
                
                .btn span {
                    font-size: 0.8rem !important;
                }
                
                /* Adjust title for mobile */
                h3 {
                    font-size: 1.5rem !important;
                }
                
                /* Better spacing for mobile */
                .mb-3 {
                    margin-bottom: 1rem !important;
                }
                
                /* Plotly graphs responsive behavior */
                .js-plotly-plot {
                    width: 100% !important;
                }
                
                /* Filter section responsive */
                .form-control, .form-select {
                    font-size: 14px !important;
                }
            }
            
            @media (max-width: 576px) {
                /* Extra small devices */
                .container-fluid {
                    padding-left: 5px !important;
                    padding-right: 5px !important;
                }
                
                h3 {
                    font-size: 1.2rem !important;
                }
                
                .btn {
                    font-size: 0.8rem !important;
                    padding: 8px !important;
                }
            }
            
            /* Ensure Plotly plots are responsive */
            .plotly-graph-div {
                width: 100% !important;
                height: auto !important;
            }
            
            /* Better legend positioning on mobile */
            @media (max-width: 768px) {
                .plotly .legend {
                    orientation: v !important;
                    x: 1.02 !important;
                    y: 1 !important;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# %%
# Callback to update figure description based on button selection
@callback(
    Output('figure-description', 'children'),
    [Input('btn-trend', 'n_clicks'),
     Input('btn-map', 'n_clicks'),
     Input('btn-age', 'n_clicks'),
     Input('btn-top10', 'n_clicks'),
     Input('btn-stats', 'n_clicks'),
     Input('btn-table', 'n_clicks')],
    prevent_initial_call=True
)
def update_figure_description(btn_trend, btn_map, btn_age, btn_top10, btn_stats, btn_table):
    """Update the figure description based on which button was clicked"""
    
    # Get which button triggered the callback
    ctx = dash.callback_context
    
    if not ctx.triggered:
        button_id = 'btn-trend'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    print(f"Button clicked: {button_id}")  # Debug print
    
    # Define descriptions for each visualization
    descriptions = {
        'btn-trend': html.Div([
            html.H6("📊 Cancer Trends", 
                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
            html.P([
                "Displays temporal trends of cancer incidence rates over multiple years. ",
                "This visualization helps identify patterns, increasing or decreasing trends, ",
                "and potential emerging concerns in cancer epidemiology."
            ], style={'line-height': '1.6', 'color': '#333'}),
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
            html.Ul([
                html.Li("Interactive line charts showing year-over-year changes"),
                html.Li("Age-standardized rates (ASR) per 100,000 population"),
                html.Li("Comparison across different cancer sites"),
                html.Li("Statistical trend analysis and projections")
            ], style={'line-height': '1.8', 'color': '#555'})
        ], style={'padding': '20px'}),
        
        'btn-map': html.Div([
            html.H6("🗺️ Regional Map", 
                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
            html.P([
                "Interactive choropleth map showing the geographic distribution of cancer incidence ",
                "across Thailand's provinces and health regions. Helps identify regional disparities ",
                "and high-risk areas for targeted public health interventions."
            ], style={'line-height': '1.6', 'color': '#333'}),
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
            html.Ul([
                html.Li("Color-coded provinces by incidence rate"),
                html.Li("Interactive hover information for each region"),
                html.Li("Animation capability to show changes over time"),
                html.Li("Health region aggregation options")
            ], style={'line-height': '1.8', 'color': '#555'})
        ], style={'padding': '20px'}),
        
        'btn-age': html.Div([
            html.H6("👥 Age Distribution", 
                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
            html.P([
                "Age-specific incidence rates showing how cancer affects different age groups. ",
                "Essential for understanding cancer burden across the lifespan and planning ",
                "age-appropriate screening and prevention programs."
            ], style={'line-height': '1.6', 'color': '#333'}),
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
            html.Ul([
                html.Li("Bar charts or pyramid plots by age group"),
                html.Li("5-year age group categorization"),
                html.Li("Comparison between male and female distributions"),
                html.Li("Peak incidence age identification")
            ], style={'line-height': '1.8', 'color': '#555'})
        ], style={'padding': '20px'}),
        
        'btn-top10': html.Div([
            html.H6("🏆 Top 10 Cancer Sites", 
                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
            html.P([
                "Ranking of the most common cancer types by incidence rate. ",
                "Provides a quick overview of the cancer burden and helps prioritize ",
                "resource allocation and prevention strategies for the most prevalent cancers."
            ], style={'line-height': '1.6', 'color': '#333'}),
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
            html.Ul([
                html.Li("Horizontal bar chart ranking by ASR"),
                html.Li("Separate rankings for male, female, and combined"),
                html.Li("Number of cases and rates displayed"),
                html.Li("Filterable by year and region")
            ], style={'line-height': '1.8', 'color': '#555'})
        ], style={'padding': '20px'}),
        
        'btn-stats': html.Div([
            html.H6("📈 Statistical Analysis", 
                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
            html.P([
                "Comprehensive statistical summary including key metrics, trends, and analytical insights. ",
                "Provides numerical evidence for policy decisions and research directions ",
                "with confidence intervals and statistical significance testing."
            ], style={'line-height': '1.6', 'color': '#333'}),
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
            html.Ul([
                html.Li("Summary cards with total cases, average ASR, and trends"),
                html.Li("Year-over-year percentage changes"),
                html.Li("Provincial and regional statistics"),
                html.Li("Prediction models and forecasting")
            ], style={'line-height': '1.8', 'color': '#555'})
        ], style={'padding': '20px'}),
        
        'btn-table': html.Div([
            html.H6("📋 Data Table", 
                   style={'color': '#005eaa', 'font-weight': '600', 'margin-bottom': '15px'}),
            html.P([
                "Detailed tabular view of raw data with sorting, filtering, and export capabilities. ",
                "Allows researchers and analysts to access precise numerical values ",
                "for further analysis or reporting purposes."
            ], style={'line-height': '1.6', 'color': '#333'}),
            html.Hr(style={'margin': '20px 0'}),
            html.H6("Key Features:", style={'color': '#0071bc', 'font-weight': '600'}),
            html.Ul([
                html.Li("Sortable columns by any field"),
                html.Li("Search and filter functionality"),
                html.Li("Pagination for large datasets"),
                html.Li("Export to CSV/Excel options")
            ], style={'line-height': '1.8', 'color': '#555'})
        ], style={'padding': '20px'})
    }
    
    return descriptions.get(button_id, descriptions['btn-trend'])


# %%
# Callback to dynamically update filter options based on button selection
@callback(
    [Output('filter-year', 'options'),
     Output('filter-site', 'options'), 
     Output('filter-sex', 'options'),
     Output('filter-region', 'options'),
     Output('filter-stage', 'options'),
     Output('filter-year', 'value'),
     Output('filter-site', 'value'),
     Output('filter-sex', 'value'),
     Output('filter-region', 'value'),
     Output('filter-stage', 'value'),
     Output('year-filter-container', 'style'),
     Output('site-filter-container', 'style'),
     Output('sex-filter-container', 'style'),
     Output('region-filter-container', 'style'),
     Output('stage-filter-container', 'style')],
    [Input('btn-trend', 'n_clicks'),
     Input('btn-map', 'n_clicks'),
     Input('btn-age', 'n_clicks'),
     Input('btn-top10', 'n_clicks'),
     Input('btn-stats', 'n_clicks'),
     Input('btn-table', 'n_clicks')],
    prevent_initial_call=True
)
def update_filter_options(btn_trend, btn_map, btn_age, btn_top10, btn_stats, btn_table):
    """Update filter options based on selected visualization using actual filter options"""
    
    # Get which button triggered the callback
    ctx = dash.callback_context
    
    if not ctx.triggered:
        button_id = 'btn-trend'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    print(f"🔄 Updating filters for: {button_id}")
    
    # Define filter configurations for each visualization type using your final filter options
    if button_id == 'btn-trend':
        # Cancer Trends - uses fig1_option: ['cancer_types', 'sex_options'] - NO YEAR FILTER
        year_options = []  # No year filter for trends (shows all years by default)
        site_options = [{'label': cancer_type, 'value': cancer_type} 
                       for cancer_type in fig1_option.get('cancer_types', [])]
        sex_options = [{'label': 'Both Sexes', 'value': 'Both'}] + \
                     [{'label': sex_opt, 'value': sex_opt} 
                      for sex_opt in fig1_option.get('sex_options', [])]
        region_options = []  # No region filter for Cancer Trends
        stage_options = []   # No stage filter for Cancer Trends
        
        # Hide year, region, stage filters for Cancer Trends, show site and sex filter
        return (year_options, site_options, sex_options, region_options, stage_options, 
                None, 'Breast', 'Both', [], [], 
                {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'})
    
    elif button_id == 'btn-map':
        # Regional Map - uses fig4_option: ['cancer_types', 'sex_options', 'years']
        year_options = []  # No year filter for map (shows all years by default)
        site_options = [{'label': cancer_type, 'value': cancer_type} 
                       for cancer_type in fig1_option.get('cancer_types', [])]
        sex_options = [{'label': 'Both Sexes', 'value': 'Both'}] + \
                     [{'label': sex_opt, 'value': sex_opt} 
                      for sex_opt in fig1_option.get('sex_options', [])]
        region_options = []  # No region filter for map
        stage_options = []   # No stage filter for map
        
        # Hide year, region, stage filters for map, show site and sex filter
        return (year_options, site_options, sex_options, region_options, stage_options,
                None, 'Breast', 'Both', [], [],
                {'display': 'none'}, {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'})
        
    
    elif button_id == 'btn-age':
        # Age Distribution - uses fig2_option: ['cancer_types'] only - NO YEAR OR SEX FILTER
        year_options = []  # No year filter for age animation (animation shows progression over years)
        site_options = [{'label': cancer_type, 'value': cancer_type} 
                       for cancer_type in fig2_option.get('cancer_types', [])]
        sex_options = []  # No sex filter for age distribution
        region_options = []  # No region filter for age distribution
        stage_options = []   # No stage filter for age distribution
        
        return (year_options, site_options, sex_options, region_options, stage_options,
                None, 'Breast', 'Both', [], [],
                {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'})
    
    elif button_id == 'btn-top10':
        # Top 10 - uses fig3_option: ['years'] only (sex and cancer_types removed)
        year_options = [{'label': str(year), 'value': int(year)} 
                       for year in fig3_option.get('years', [])]
        site_options = []  # No cancer site filter for Top 10 (shows all sites)
        sex_options = []   # No sex filter for Top 10 
        
        default_year = year_options[0]['value'] if year_options else 2020
        return (year_options, site_options, sex_options, default_year, 'all', 'Both', {'display': 'block'}, {'display': 'none'}, {'display': 'none'})
    
    elif button_id == 'btn-stats':
        # Survival Analysis - uses fig5_option: ['cancer_types', 'health_regions', 'stages']
        year_options = []  # No year filter for survival data
        site_options = [{'label': cancer_type.title(), 'value': cancer_type} 
                       for cancer_type in fig5_option.get('cancer_types', [])]
        sex_options = []   # No sex filter for survival data
        region_options = [{'label': f'Region {region}', 'value': region} 
                         for region in fig5_option.get('health_regions', [])] + \
                        [{'label': 'All Regions', 'value': 'all'}]
        stage_options = [{'label': stage.title(), 'value': stage} 
                        for stage in fig5_option.get('stages', [])]
        
        # Show cancer site, region, and stage filters for survival data
        return (year_options, site_options, sex_options, region_options, stage_options,
                None, 'breast', 'Both', ['all', '2'], ['stage1', 'stage2', 'stage3', 'stage4'],
                {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'})
    
    elif button_id == 'btn-table':
        # Data Table - uses fig1_option: ['cancer_types', 'sex_options'] + specific year
        year_options = [{'label': '2020', 'value': 2020}, 
                       {'label': '2019', 'value': 2019}, 
                       {'label': '2018', 'value': 2018}]
        site_options = [{'label': cancer_type, 'value': cancer_type} 
                       for cancer_type in fig1_option.get('cancer_types', [])]
        sex_options = [{'label': 'Both Sexes', 'value': 'Both'}] + \
                     [{'label': sex_opt, 'value': sex_opt} 
                      for sex_opt in fig1_option.get('sex_options', [])]
        
        return (year_options, site_options, sex_options, 2020, 'Breast', 'Both', {'display': 'block'}, {'display': 'block'}, {'display': 'block'})
    
    # Default fallback (Cancer Trends)
    year_options = [{'label': 'All Years', 'value': 'all'}]
    site_options = [{'label': cancer_type, 'value': cancer_type} 
                   for cancer_type in fig1_option.get('cancer_types', [])]
    sex_options = [{'label': 'Both Sexes', 'value': 'Both'}] + \
                 [{'label': sex_opt, 'value': sex_opt} 
                  for sex_opt in fig1_option.get('sex_options', [])]
    
    return (year_options, site_options, sex_options, 'all', 'Breast', 'Both', {'display': 'block'}, {'display': 'block'}, {'display': 'block'})

# %%
# Simplified responsive callback - shorter version
_last_selected_viz = 'btn-trend'

# Enhanced responsive config for better web responsiveness
RESPONSIVE_CONFIG = {
    'responsive': True, 
    'displayModeBar': True, 
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'cancer_data_viz',
        'height': 600,
        'width': 1000,
        'scale': 2
    }
}

# Enhanced responsive style with better mobile support
RESPONSIVE_STYLE = {
    'width': '100%', 
    'height': '70vh', 
    'min-height': '500px',
    'max-height': '800px'
}

# Responsive layout config for Plotly figures
RESPONSIVE_LAYOUT = {
    'autosize': True,
    'margin': dict(l=50, r=50, t=80, b=80),
    'font': {'size': 12},
    'title': {'x': 0.5, 'xanchor': 'center'},
    'xaxis': {
        'automargin': True,
        'title': {'standoff': 20}
    },
    'yaxis': {
        'automargin': True,
        'title': {'standoff': 20}
    },
    'legend': {
        'orientation': 'h',
        'yanchor': 'bottom',
        'y': -0.3,
        'xanchor': 'center',
        'x': 0.5
    }
}

@callback(
    Output('content-area', 'children'),
    [Input('btn-trend', 'n_clicks'),
     Input('btn-map', 'n_clicks'),
     Input('btn-age', 'n_clicks'),
     Input('btn-top10', 'n_clicks'),
     Input('btn-stats', 'n_clicks'),
     Input('btn-table', 'n_clicks'),
     Input('btn-apply-filters', 'n_clicks'),
     Input('filter-year', 'value'),
     Input('filter-site', 'value'),
     Input('filter-sex', 'value'),
     Input('filter-region', 'value'),
     Input('filter-stage', 'value')],
    prevent_initial_call=True
)
def update_content(btn_trend, btn_map, btn_age, btn_top10, btn_stats, btn_table, btn_apply, year, site, sex, regions, stages):
    global _last_selected_viz
    ctx = dash.callback_context
    
    if not ctx.triggered:
        button_id = 'btn-trend'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id in ['btn-trend', 'btn-map', 'btn-age', 'btn-top10', 'btn-stats', 'btn-table']:
        _last_selected_viz = button_id
    elif button_id == 'btn-apply-filters':
        button_id = _last_selected_viz
    
    print(f"Button: {button_id}, Site: {site}, Sex: {sex}")
    
    # Simple responsive graphs for each visualization
    if button_id == 'btn-trend':
        try:
            fig = gen_graph.create_trend_graph_with_future_prediction(asr1, selected_sex=sex, selected_cancer=site, future_years=[2023, 2026, 2030])
            # Apply responsive layout
            fig.update_layout(**RESPONSIVE_LAYOUT)
            return html.Div([
                html.H4("📊 Cancer Trends", style={'color': '#005eaa'}),
                dcc.Graph(
                    figure=fig, 
                    config=RESPONSIVE_CONFIG, 
                    style=RESPONSIVE_STYLE,
                    responsive=True
                )
            ])
        except Exception as e:
            return html.Div([html.H4("Error", style={'color': '#dc3545'}), html.P(str(e))])
    
    elif button_id == 'btn-map':
        try:
            fig = gen_graph.create_map_healthregion(asr3, prov_hr, site=site, sex=sex)
            # Apply responsive layout with map-specific settings
            map_layout = RESPONSIVE_LAYOUT.copy()
            map_layout.update({
                'geo': {
                    'projection': {'type': 'mercator'},
                    'showframe': False,
                    'showcoastlines': True
                }
            })
            fig.update_layout(**map_layout)
            return html.Div([
                html.H4("🗺️ Regional Map", style={'color': '#005eaa'}),
                dcc.Graph(
                    figure=fig, 
                    config=RESPONSIVE_CONFIG, 
                    style=RESPONSIVE_STYLE,
                    responsive=True
                )
            ])
        except Exception as e:
            return html.Div([html.H4("Error", style={'color': '#dc3545'}), html.P(str(e))])
    
    elif button_id == 'btn-age':
        try:
            fig = gen_graph.create_animated_age_distribution_graph(asr2, selected_cancer=site)
            # Apply responsive layout
            fig.update_layout(**RESPONSIVE_LAYOUT)
            return html.Div([
                html.H4("👥 Age Distribution", style={'color': '#005eaa'}),
                dcc.Graph(
                    figure=fig, 
                    config=RESPONSIVE_CONFIG, 
                    style=RESPONSIVE_STYLE,
                    responsive=True
                )
            ])
        except Exception as e:
            return html.Div([html.H4("Error", style={'color': '#dc3545'}), html.P(str(e))])
    
    elif button_id == 'btn-top10':
        try:
            fig = gen_graph.create_top10_cancer_bar_graph(asr1, selected_year=year)
            # Apply responsive layout
            fig.update_layout(**RESPONSIVE_LAYOUT)
            return html.Div([
                html.H4("🏆 Top 10 Cancers", style={'color': '#005eaa'}),
                dcc.Graph(
                    figure=fig, 
                    config=RESPONSIVE_CONFIG, 
                    style=RESPONSIVE_STYLE,
                    responsive=True
                )
            ])
        except Exception as e:
            return html.Div([html.H4("Error", style={'color': '#dc3545'}), html.P(str(e))])
    
    elif button_id == 'btn-stats':
        try:
            selected_regions = regions[:3] if regions and len(regions) > 3 else (regions or ['all', '2'])
            selected_stages = stages[:4] if stages and len(stages) > 4 else (stages or ['stage1', 'stage2', 'stage3', 'stage4'])
            fig = gen_graph.create_survival_line_plot(df=surv, selected_regions=selected_regions, selected_cancer=site, selected_stages=selected_stages)
            # Apply responsive layout
            fig.update_layout(**RESPONSIVE_LAYOUT)
            return html.Div([
                html.H4("📈 Survival Analysis", style={'color': '#005eaa'}),
                dcc.Graph(
                    figure=fig, 
                    config=RESPONSIVE_CONFIG, 
                    style=RESPONSIVE_STYLE,
                    responsive=True
                )
            ])
        except Exception as e:
            return html.Div([html.H4("Error", style={'color': '#dc3545'}), html.P(str(e))])
    
    elif button_id == 'btn-table':
        return html.Div([
            html.H4("📋 Data Table", style={'color': '#005eaa'}),
            dbc.Table([
                html.Thead(html.Tr([html.Th("Province"), html.Th("Cases"), html.Th("ASR")])),
                html.Tbody([
                    html.Tr([html.Td("Bangkok"), html.Td("1,234"), html.Td("35.2")]),
                    html.Tr([html.Td("Chiang Mai"), html.Td("567"), html.Td("28.5")])
                ])
            ], bordered=True, responsive=True)
        ])
    
    return html.Div([html.P("Select a visualization", className="text-center text-muted")])

#add datetime 
import datetime
now = datetime.datetime.now()
#show datetime in the webpage
#app.index_string = app.index_string.replace('</body>', f'<div style="text-align:center; font-size:0.8rem; color:#666; margin-top:10px;">Last updated: {now.strftime("%Y-%m-%d %H:%M:%S")}</div></body>')
#display  'Created by NCI Data Viz Team' at the bottom of the page
app.index_string = app.index_string.replace('</body>', '<div style="text-align:center; font-size:0.8rem; color:#666; margin-top:5px;">Created by NCI Data Viz Team</div></body>')


# %%
# Run the app
if __name__ == '__main__':
    # Check if running in Jupyter notebook
    try:
        # Use a different port to avoid conflicts
        app.run(debug=False, port=8051,host='0.0.0.0', use_reloader=True)
        
    except Exception as e:
        print(f"Error starting app: {e}")
        print("App may already be running. Please restart the kernel if needed.")



