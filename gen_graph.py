# %%
# graph_functions.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots
import dataloader
import json
import nbformat
import os 

folder = 'data/'
with open(os.path.join(folder, 'provinces.geojson'), 'r', encoding='utf-8') as f:
    thai_geojson = json.load(f)
prov_hr=pd.read_excel(os.path.join(folder, 'provice_healthregion.xlsx'))
prov_hr['provine_code']=prov_hr['provine_code'].astype(str)
prov_hr['health_region']=prov_hr['health_region'].astype(str)

# %% [markdown]
# ### Graph 1 

# %%
def create_trend_graph_with_future_prediction(df, selected_sex, selected_cancer, future_years=[2023, 2026]):
    """
    Create ASR trend graph with predictions for future years
    
    Args:
        df (DataFrame): Input dataframe
        selected_sex (str): Selected sex filter
        selected_cancer (str): Selected cancer type filter
        future_years (list): List of future years to predict
    
    Returns:
        plotly.graph_objects.Figure: Trend line graph with future predictions
    """
    if not selected_sex or not selected_cancer:
        return go.Figure().add_annotation(
            text="Please select both sex and cancer type",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    df['Year'] = df['Year'].astype(int)

    if selected_sex == 'Both':
        # Filter data
        filtered_df = df[
            (df['Site'] == selected_cancer)
        ].copy()
        #we need to sum asr for both group by year, cancer type
        filtered_df = filtered_df.groupby(['Year', 'Site']).agg({'ASR World': 'sum'}).reset_index()
    else:
        filtered_df = df[
            (df['Sex'] == selected_sex) & 
            (df['Site'] == selected_cancer)
        ].copy()

    #round ASR World to 2 decimal places
    filtered_df['ASR World'] = filtered_df['ASR World'].round(3)

    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Group by year and calculate mean ASR
    trend_data = filtered_df.groupby('Year')['ASR World'].mean().reset_index()
    
    if len(trend_data) >= 2:  # Need at least 2 points for regression
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        
        # Prepare historical data for regression
        X_historical = trend_data[['Year']].values
        y_historical = trend_data['ASR World'].values
        
        # Scale the features
        scaler = StandardScaler()
        X_historical_scaled = scaler.fit_transform(X_historical)
        
        # Fit linear regression model
        model = LinearRegression()
        model.fit(X_historical_scaled, y_historical)
        
        # Generate predictions for historical data
        trend_data['Predicted ASR World'] = model.predict(X_historical_scaled)
        #round predicted ASR World to 2 decimal places
        trend_data['Predicted ASR World'] = trend_data['Predicted ASR World'].round(3)
        
        # Create future data points
        future_data = pd.DataFrame({'Year': future_years})
        X_future = future_data[['Year']].values
        X_future_scaled = scaler.transform(X_future)  # Use same scaler
        future_predictions = model.predict(X_future_scaled)
        #round future predictions to 2 decimal places
        future_predictions = future_predictions.round(3)
        
        future_data['ASR World'] = future_predictions
        future_data['Predicted ASR World'] = future_predictions
        
        # Combine historical and future data
        all_years = list(trend_data['Year']) + future_years
        all_actual = list(trend_data['ASR World']) + [None] * len(future_years)
        all_predicted = list(trend_data['Predicted ASR World']) + list(future_predictions)
        
        # Create figure
        fig = go.Figure()
        
        # Add historical actual data
        fig.add_trace(go.Scatter(
            x=trend_data['Year'],
            y=trend_data['ASR World'],
            mode='lines+markers',
            name='Historical ASR',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        # Add historical predicted data
        fig.add_trace(go.Scatter(
            x=trend_data['Year'],
            y=trend_data['Predicted ASR World'],
            mode='lines',
            name='Fitted Model',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            opacity=0.7
        ))
        
        # Add connection line from last historical point to first future prediction
        fig.add_trace(go.Scatter(
            x=[trend_data['Year'].iloc[-1], future_years[0]],
            y=[trend_data['Predicted ASR World'].iloc[-1], future_predictions[0]],
            mode='lines',
            name='Connection',
            line=dict(color='#2ca02c', width=2, dash='dot'),
            opacity=0.6,
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add future predictions
        fig.add_trace(go.Scatter(
            x=future_years,
            y=list(future_predictions),
            mode='lines+markers',
            name='Future Predictions',
            line=dict(color='#2ca02c', width=3, dash='dot'),
            marker=dict(size=10, symbol='diamond'),
            opacity=0.8
        ))
        
        # Calculate R² score for model performance on historical data
        from sklearn.metrics import r2_score
        r2 = r2_score(y_historical, trend_data['Predicted ASR World'])
        
        # Create prediction summary text with R² score at the top
        prediction_text = f"R² Score: {r2:.3f}<br><br>Future Predictions:<br>"
        for year, pred in zip(future_years, future_predictions):
            prediction_text += f"Year {year}: {round(pred, 2)}<br>"
        
        fig.update_layout(
            title=f'Cancer incidence trend with future predictions for {selected_cancer} and ({selected_sex} )sex',
            xaxis_title="Year",
            yaxis_title="ASR (per 100,000)",
            hovermode='x unified',
            template='plotly_white',
            title_font_size=18,
            title_x=0.5,
            autosize=True,
            margin=dict(l=50, r=150, t=80, b=60),  # Responsive margins
            yaxis=dict(
                range=[0, max(max(trend_data['ASR World']), max(future_predictions)) * 1.1],
                automargin=True
            ),
            xaxis=dict(automargin=True),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=10) 
            ),
            annotations=[
                dict(
                    text=prediction_text,
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,  # Moved to top-left for mobile compatibility
                    showarrow=False,
                    align="left",
                    xanchor="left",
                    yanchor="top",
                    borderwidth=1,
                    bordercolor="gray",
                    bgcolor="rgba(255,255,255,0.9)",
                    font=dict(size=10)
                )
            ]
        )
        
        # Print predictions to console as well
        #print(f"\nFuture ASR Predictions for {selected_cancer} ({selected_sex}):")
        #print(f"Model R² Score: {r2:.3f}")
        #print("-" * 40)
        #for year, pred in zip(future_years, future_predictions):
        #    print(f"Year {year}: {pred:.2f}")
        #print("-" * 40)
        
        return fig
        
    else:
        return go.Figure().add_annotation(
            text="Insufficient data for prediction (need at least 2 data points)",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )


def create_animated_age_distribution_graph(df, selected_cancer):
    """
    Create animated ASR age distribution showing changes over years
    
    Args:
        df (DataFrame): Input dataframe with Year column
        selected_cancer (str): Selected cancer type filter
    
    Returns:
        plotly.graph_objects.Figure: Animated age distribution graph
    """
    if not selected_cancer:
        return go.Figure().add_annotation(
            text="Please select a cancer type",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Filter data for selected cancer
    filtered_df = df[df['Site'] == selected_cancer].copy()
    filtered_df['ASR'] = filtered_df['ASR'].round(3)
    
    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data available for selected cancer type",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Check if we have age group data
    if 'Age_Group' in filtered_df.columns and not filtered_df['Age_Group'].isna().all():
        # Define age group order
        desired_order = ['0-','5-','10-','15-','20-','25-','30-','35-','40-','45-',
                        '50-','55-','60-','65-','70-','75+']
        
        order_mapping = {age_group: idx for idx, age_group in enumerate(desired_order)}
        
        def sort_age_groups(age_group):
            if pd.isna(age_group):
                return 999
            age_str = str(age_group).strip()
            return order_mapping.get(age_str, 1000)
        
        # Get unique years for animation
        years = sorted(filtered_df['Year'].unique())
        
        # Check if we have both male and female data
        if 'Sex' in filtered_df.columns and filtered_df['Sex'].nunique() > 1:
            # Prepare animation data for both sexes
            animation_data = []
            
            for year in years:
                year_data = filtered_df[filtered_df['Year'] == year]
                
                # Process male data
                male_data = year_data[year_data['Sex'] == 'Male'].groupby('Age_Group')['ASR'].mean().reset_index()
                if len(male_data) > 0:
                    male_data['sort_key'] = male_data['Age_Group'].apply(sort_age_groups)
                    male_data = male_data.sort_values('sort_key').drop('sort_key', axis=1)
                    male_data['Sex'] = 'Male'
                    male_data['Year'] = year
                    animation_data.append(male_data)
                
                # Process female data
                female_data = year_data[year_data['Sex'] == 'Female'].groupby('Age_Group')['ASR'].mean().reset_index()
                if len(female_data) > 0:
                    female_data['sort_key'] = female_data['Age_Group'].apply(sort_age_groups)
                    female_data = female_data.sort_values('sort_key').drop('sort_key', axis=1)
                    female_data['Sex'] = 'Female'
                    female_data['Year'] = year
                    animation_data.append(female_data)
            
            if not animation_data:
                return go.Figure().add_annotation(
                    text="No age group data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    font=dict(size=16, color="gray")
                )
            
            # Combine all years data
            final_df = pd.concat(animation_data, ignore_index=True)
            
            # Get all available age groups
            all_age_groups = final_df['Age_Group'].unique()
            ordered_age_groups = [age for age in desired_order if age in all_age_groups]
            
            # Calculate global max for consistent y-axis
            global_max = final_df['ASR'].max()
            
            # Create animated scatter plot
            fig = px.line(
                final_df,
                x='Age_Group',
                y='ASR',
                color='Sex',
                animation_frame='Year',
                color_discrete_map={
                    'Male': 'rgba(31, 119, 180, 1)',
                    'Female': 'rgba(255, 127, 14, 1)'
                },
                category_orders={'Age_Group': ordered_age_groups},
                range_y=[0, global_max * 1.1]
            )
            
            # Update traces to add fill and markers
            for i, trace in enumerate(fig.data):
                if trace.name == 'Male':
                    trace.update(
                        fill='tozeroy',
                        fillcolor='rgba(31, 119, 180, 0.3)',
                        line=dict(width=3, shape='spline'),
                        mode='lines+markers',
                        marker=dict(size=8, symbol='circle')
                    )
                elif trace.name == 'Female':
                    trace.update(
                        fill='tozeroy',
                        fillcolor='rgba(255, 127, 14, 0.3)',
                        line=dict(width=3, shape='spline'),
                        mode='lines+markers',
                        marker=dict(size=8, symbol='diamond')
                    )
            
            # Update frames for consistent styling
            for frame in fig.frames:
                for i, trace in enumerate(frame.data):
                    if trace.name == 'Male':
                        trace.update(
                            fill='tozeroy',
                            fillcolor='rgba(31, 119, 180, 0.3)',
                            line=dict(width=3, shape='spline'),
                            mode='lines+markers',
                            marker=dict(size=8, symbol='circle')
                        )
                    elif trace.name == 'Female':
                        trace.update(
                            fill='tozeroy',
                            fillcolor='rgba(255, 127, 14, 0.3)',
                            line=dict(width=3, shape='spline'),
                            mode='lines+markers',
                            marker=dict(size=8, symbol='diamond')
                        )
            
            fig.update_layout(
                title=dict(
                    text=f'🎬 Age Distribution Animation: {selected_cancer} - Male vs Female',
                    font=dict(size=20),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="Age Group",
                yaxis_title="Age-Standardized Rate (ASR)",
                template='plotly_white',
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=150),  # More space for lower slider
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12)
                ),
                # Animation controls
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'y': 1.02,  # Moved above the plot area
                    'x': 0.02,  # Far left position
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'bgcolor': 'lightblue',
                    'borderwidth': 2,
                    'font': {'size': 12, 'color': 'darkblue'},  # Slightly smaller font
                    'buttons': [
                        {
                            'label': '▶️ Play Animation',
                            'method': 'animate',
                            'args': [None, {
                                'frame': {'duration': 3000, 'redraw': True},
                                'fromcurrent': True,
                                'transition': {'duration': 1500}
                            }]
                        },
                        {
                            'label': '⏸️ Pause',
                            'method': 'animate',
                            'args': [[None], {
                                'frame': {'duration': 0, 'redraw': False},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }]
                        },
                        {
                            'label': '⏮️ Reset',
                            'method': 'animate',
                            'args': [[str(years[0])], {
                                'frame': {'duration': 0, 'redraw': True},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }]
                        }
                    ]
                }]
            )
            
            # Customize slider
            fig.layout.sliders[0].currentvalue.prefix = "📅 Year: "
            fig.layout.sliders[0].currentvalue.font.size = 16
            fig.layout.sliders[0].currentvalue.font.color = "darkblue"
            fig.layout.sliders[0].y = -0.35  # Move slider lower to avoid legend
            fig.layout.sliders[0].len = 0.8  # Make slider shorter
            fig.layout.sliders[0].x = 0.1    # Center the shorter slider
            
            # Add year annotations for each frame
            for frame in fig.frames:
                year = frame.name
                frame.layout.annotations = [
                    dict(
                        text=f"📅 {year}",
                        xref="paper", yref="paper",
                        x=0.02, y=0.98,
                        showarrow=False,
                        font=dict(size=20, color="darkblue", family="Arial Black"),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="darkblue",
                        borderwidth=2
                    )
                ]
            
        else:
            # Single sex or combined data animation
            animation_data = []
            
            for year in years:
                year_data = filtered_df[filtered_df['Year'] == year]
                age_data = year_data.groupby('Age_Group')['ASR'].mean().reset_index()
                
                if len(age_data) > 0:
                    age_data['sort_key'] = age_data['Age_Group'].apply(sort_age_groups)
                    age_data = age_data.sort_values('sort_key').drop('sort_key', axis=1)
                    age_data['Year'] = year
                    animation_data.append(age_data)
            
            if not animation_data:
                return go.Figure().add_annotation(
                    text="No age group data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    font=dict(size=16, color="gray")
                )
            
            final_df = pd.concat(animation_data, ignore_index=True)
            all_age_groups = final_df['Age_Group'].unique()
            ordered_age_groups = [age for age in desired_order if age in all_age_groups]
            global_max = final_df['ASR'].max()
            
            # Create animated line chart
            fig = px.line(
                final_df,
                x='Age_Group',
                y='ASR',
                animation_frame='Year',
                category_orders={'Age_Group': ordered_age_groups},
                range_y=[0, global_max * 1.1]
            )
            
            # Update trace styling
            for trace in fig.data:
                trace.update(
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.3)',
                    line=dict(color='rgba(31, 119, 180, 1)', width=3, shape='spline'),
                    mode='lines+markers',
                    marker=dict(size=8, color='red', symbol='circle')
                )
            
            # Update frames styling
            for frame in fig.frames:
                for trace in frame.data:
                    trace.update(
                        fill='tozeroy',
                        fillcolor='rgba(31, 119, 180, 0.3)',
                        line=dict(color='rgba(31, 119, 180, 1)', width=3, shape='spline'),
                        mode='lines+markers',
                        marker=dict(size=8, color='red', symbol='circle')
                    )
            
            fig.update_layout(
                title=dict(
                    text=f'🎬 Age Distribution Animation: {selected_cancer}',
                    font=dict(size=20),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="Age Group",
                yaxis_title="Age-Standardized Rate (ASR)",
                template='plotly_white',
                autosize=True,
                margin=dict(l=50, r=50, t=80, b=140),  # More space for lower slider
                hovermode='x unified',
                showlegend=False,
                # Animation controls
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'y': 1.02,  # Moved above the plot area
                    'x': 0.02,  # Far left position
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'bgcolor': 'lightgreen',
                    'borderwidth': 2,
                    'font': {'size': 12, 'color': 'darkgreen'},  # Slightly smaller font
                    'buttons': [
                        {
                            'label': '▶️ Play Animation',
                            'method': 'animate',
                            'args': [None, {
                                'frame': {'duration': 3000, 'redraw': True},
                                'fromcurrent': True,
                                'transition': {'duration': 1500}
                            }]
                        },
                        {
                            'label': '⏸️ Pause',
                            'method': 'animate',
                            'args': [[None], {
                                'frame': {'duration': 0, 'redraw': False},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }]
                        },
                        {
                            'label': '⏮️ Reset',
                            'method': 'animate',
                            'args': [[str(years[0])], {
                                'frame': {'duration': 0, 'redraw': True},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }]
                        }
                    ]
                }]
            )
            
            # Customize slider
            fig.layout.sliders[0].currentvalue.prefix = "📅 Year: "
            fig.layout.sliders[0].currentvalue.font.size = 16
            fig.layout.sliders[0].currentvalue.font.color = "darkgreen"
            fig.layout.sliders[0].y = -0.25  # Move slider lower (no legend in single sex view)
            fig.layout.sliders[0].len = 0.8  # Make slider shorter
            fig.layout.sliders[0].x = 0.1    # Center the shorter slider
            
            # Add year annotations
            for frame in fig.frames:
                year = frame.name
                frame.layout.annotations = [
                    dict(
                        text=f"📅 {year}",
                        xref="paper", yref="paper",
                        x=0.02, y=0.98,
                        showarrow=False,
                        font=dict(size=20, color="darkgreen", family="Arial Black"),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="darkgreen",
                        borderwidth=2
                    )
                ]
        
        # Common styling for both cases
        fig.update_xaxes(
            tickangle=-45,
            title_font=dict(size=14),
            tickfont=dict(size=12)
        )
        fig.update_yaxes(
            title_font=dict(size=14),
            tickfont=dict(size=12)
        )
        
    else:
        # If no age group data, show by sex over years
        years = sorted(filtered_df['Year'].unique())
        animation_data = []
        
        for year in years:
            year_data = filtered_df[filtered_df['Year'] == year]
            sex_data = year_data.groupby('Sex')['ASR'].mean().reset_index()
            sex_data['Year'] = year
            animation_data.append(sex_data)
        
        if not animation_data:
            return go.Figure().add_annotation(
                text="No data available for animation",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16, color="gray")
            )
        
        final_df = pd.concat(animation_data, ignore_index=True)
        global_max = final_df['ASR'].max()
        
        fig = px.bar(
            final_df,
            x='Sex',
            y='ASR',
            animation_frame='Year',
            color='Sex',
            color_discrete_map={
                'Male': 'rgba(31, 119, 180, 0.7)',
                'Female': 'rgba(255, 127, 14, 0.7)'
            },
            range_y=[0, global_max * 1.1]
        )
        
        fig.update_layout(
            title=dict(
                text=f'🎬 ASR by Sex Animation: {selected_cancer}',
                font=dict(size=20),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Sex",
            yaxis_title="Age-Standardized Rate (ASR)",
            template='plotly_white',
            height=600,
            width=800,
            margin=dict(l=60, r=60, t=100, b=80),
            showlegend=False,
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'y': -0.15,
                'x': 0.9,
                'xanchor': 'right',
                'yanchor': 'bottom',
                'bgcolor': 'lightcoral',
                'borderwidth': 2,
                'font': {'size': 14, 'color': 'darkred'},
                'buttons': [
                    {
                        'label': '▶️ Play Animation',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 2500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 1200}
                        }]
                    },
                    {
                        'label': '⏸️ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }]
        )
        
        fig.layout.sliders[0].currentvalue.prefix = "📅 Year: "
        fig.layout.sliders[0].currentvalue.font.size = 16
        fig.layout.sliders[0].currentvalue.font.color = "darkred"
    
    return fig




# %%
# Updated function to show horizontal bar graph with top 10 cancer for male and female in subplots
def create_top10_cancer_bar_graph(df, selected_year):
    """
    Create horizontal bar graph showing top 10 cancers for male and female in separate subplots
    
    Args:
        df (DataFrame): Input dataframe
        selected_year (int): Selected year filter
        
    Returns:
        plotly.graph_objects.Figure: Horizontal bar graph with two subplots for top 10 cancers
    """
    if selected_year is None:
        display_year = df['Year'].max() if 'Year' in df.columns else 2020
    else:
        display_year = selected_year
    
    # Filter data for selected year and exclude "All sites"
    filtered_df = df[
        (df['Year'] == display_year) & 
        (df['Site'] != 'All sites')
    ].copy()
    
    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data available for selected year",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Get data for both genders
    male_data = filtered_df[filtered_df['Sex'] == 'Male']
    female_data = filtered_df[filtered_df['Sex'] == 'Female']

    if len(male_data) == 0 and len(female_data) == 0:
        return go.Figure().add_annotation(
            text="No data available for selected year",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Create subplots with 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Male', 'Female'),
        horizontal_spacing=0.10,
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Process Male data
    if len(male_data) > 0:
        # Use the correct column name based on your data structure
        asr_column = 'ASR World' if 'ASR World' in male_data.columns else 'ASR'
        
        # Get top 10 cancers for males (excluding "All sites")
        top_male_cancers = male_data.nlargest(10, asr_column)
        
        # Add male data to first subplot
        fig.add_trace(
            go.Bar(
                y=top_male_cancers['Site'],
                x=top_male_cancers[asr_column],
                orientation='h',
                name='Male',
                marker=dict(
                    color='rgba(31, 119, 180, 0.7)',  # Blue for male
                    line=dict(color='rgba(31, 119, 180, 1.0)', width=1)
                ),
                hovertemplate='<b>%{y}</b><br>ASR: %{x:.2f}<extra></extra>',
                text=top_male_cancers[asr_column].round(2),
                textposition='outside',
                textfont=dict(color='Black', size=10)
            ),
            row=1, col=1
        )
    
    # Process Female data
    if len(female_data) > 0:
        # Use the correct column name based on your data structure
        asr_column = 'ASR World' if 'ASR World' in female_data.columns else 'ASR'
        
        # Get top 10 cancers for females (excluding "All sites")
        top_female_cancers = female_data.nlargest(10, asr_column)
        
        # Add female data to second subplot
        fig.add_trace(
            go.Bar(
                y=top_female_cancers['Site'],
                x=top_female_cancers[asr_column],
                orientation='h',
                name='Female',
                marker=dict(
                    color='rgba(255, 127, 14, 0.7)',  # Orange for female
                    line=dict(color='rgba(255, 127, 14, 1.0)', width=1)
                ),
                hovertemplate='<b>%{y}</b><br>ASR: %{x:.2f}<extra></extra>',
                text=top_female_cancers[asr_column].round(2),
                textposition='outside',
                textfont=dict(color='Black', size=10)
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title=f'Top 10 Cancers by ASR - Male vs Female ({display_year})',
        template='plotly_white',
        title_font_size=18,
        title_x=0.5,
        autosize=True,
        showlegend=False,
        margin=dict(l=180, r=30, t=80, b=50),  # Reduced left margin for mobile
        font=dict(size=10),
        bargap=0.02  # Very close bars
    )
    #set x axis range to start from 0 and end at max asr + 10%
    max_asr = max(top_male_cancers[asr_column].max(), top_female_cancers[asr_column].max())
    fig.update_xaxes(range=[0, max_asr * 1.1], row=1, col=1)
    fig.update_xaxes(range=[0, max_asr * 1.1], row=1, col=2)

    # Update x-axis titles
    fig.update_xaxes(title_text="Age-Standardized Rate (ASR)", row=1, col=1, title_font=dict(size=12))
    fig.update_xaxes(title_text="Age-Standardized Rate (ASR)", row=1, col=2, title_font=dict(size=12))
    
    # Update y-axis titles and reverse order for horizontal bars
    fig.update_yaxes(
        #title_text="Cancer Type", 
        autorange="reversed", 
        row=1, col=1,
        tickfont=dict(size=11),
        title_font=dict(size=14)
    )
    fig.update_yaxes(
        #title_text="Cancer Type", 
        autorange="reversed", 
        row=1, col=2,
        tickfont=dict(size=11),
        title_font=dict(size=14)
    )
    
    return fig



# %%
def create_map_healthregion(df, prov_hr, site, sex):
    df_filtered = df[(df['Site'] == site)].copy()
    if sex != 'Both sex':
        df_filtered = df_filtered[df_filtered['Sex'] == sex]
        df_merged=pd.merge(prov_hr, df_filtered, left_on='health_region', right_on='healthregion', how='left')
    else:
        df_filtered = df_filtered.groupby(['healthregion']).agg({'ASR World': 'sum'}).reset_index()
        df_merged=pd.merge(prov_hr, df_filtered, left_on='health_region', right_on='healthregion', how='left')
    fig = px.choropleth_map(
        df_merged,
        geojson=thai_geojson,
        locations='provine_code',
        featureidkey='properties.pro_code',
        color='ASR World',
        color_continuous_scale='Blues',
        #hover_name='healthregion',
        hover_data={'health_region': True, 'ASR World': ':.2f', 'provine_code': False, 'province': True},
        #hover_data={'ASR World': ':.2f'},
        center={"lat": 13.4, "lon": 100.523186},
        map_style="carto-voyager-nolabels", zoom=5,
        range_color=[df_merged['ASR World'].min(), df_merged['ASR World'].max()],
        #title=f'ASR of {site} of {sex} by Health Region'
    )
    #margin={"r":0,"t":0,"l":0,"b":0}
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},
        autosize=True,
        title_font_size=14, 
        title_x=0.5, 
        title_text=f'ASR of {site} cancer of {sex} by Health Region : Year 2020'
    )
    #add figure title
    #fig.update_layout(title_font_size=10, title_x=0.5, title_text='US State Population by State')
    return fig



# %%
def create_survival_line_plot(df, selected_regions, selected_cancer, selected_stages):
    """
    Create survival line plot with time on x-axis and survival time on y-axis
    
    Args:
        df (DataFrame): Survival dataframe with columns: time, region, cancer, stage, surv_time
        selected_regions (list): List of selected regions (max 3)
        selected_cancer (str): Selected cancer type
        selected_stages (list): List of selected stages
    
    Returns:
        plotly.graph_objects.Figure: Line plot showing survival curves
    """
    
    # Input validation
    if not selected_regions or not selected_cancer or not selected_stages:
        return go.Figure().add_annotation(
            text="Please select region(s), cancer type, and stage(s)",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Limit regions to maximum 3
    if len(selected_regions) > 3:
        selected_regions = selected_regions[:3]
        print(f"⚠️ Maximum 3 regions allowed. Using first 3: {selected_regions}")
    
    # Filter data based on selections
    filtered_df = df[
        (df['region'].isin(selected_regions)) &
        (df['cancer'] == selected_cancer) &
        (df['stage'].isin(selected_stages))
    ].copy()
    
    if filtered_df.empty:
        return go.Figure().add_annotation(
            text="No data available for selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
    
    # Create figure
    fig = go.Figure()
    
    # Define bold, high-contrast colors for stages - FIXED mapping per stage
    stage_colors = {
        'stage1': '#00AA00',   # Dark Green (excellent survival)
        'stage2': '#FF6600',   # Dark Orange (good survival)  
        'stage3': '#CC0000',   # Dark Red (moderate survival)
        'stage4': '#6600CC'    # Dark Purple (poor survival)
    }
    
    # Define line styles based on selection order (1st=solid, 2nd=short dot, 3rd=dot-medium dash)
    selection_order_styles = [
        dict(dash='solid', width=2),           # 1st selected region: Solid
        dict(dash='3,3', width=2),             # 2nd selected region: Short dot  
        dict(dash='10,3', width=2)          # 3rd selected region: Dot-medium dash
    ]
    
    # Define larger, more distinct symbols for stages
    stage_symbols = {
        'stage1': 'circle',
        'stage2': 'square',
        'stage3': 'diamond',
        'stage4': 'triangle-up'
    }
    
    # Define larger marker sizes for stages
    stage_marker_sizes = {
        'stage1': 12,
        'stage2': 12,
        'stage3': 12,
        'stage4': 12
    }
    
    # Add traces for each region-stage combination
    for region_idx, region in enumerate(selected_regions):
        for stage in selected_stages:
            # Filter for specific region and stage
            subset = filtered_df[
                (filtered_df['region'] == region) & 
                (filtered_df['stage'] == stage)
            ].copy()
            
            if not subset.empty:
                # Sort by time
                subset = subset.sort_values('time')
                
                # Get color and style based on selection order
                color = stage_colors.get(stage, '#1f77b4')
                # Use selection order index to get line style (with fallback for >3 regions)
                line_style = selection_order_styles[region_idx] if region_idx < len(selection_order_styles) else dict(dash='solid', width=2)
                symbol = stage_symbols.get(stage, 'circle')
                marker_size = stage_marker_sizes.get(stage, 10)
                
                # Create trace name
                region_name = f"Region {region}" if region != 'all' else "All Regions"
                trace_name = f"{stage.capitalize()} - {region_name}"
                
                # Add line trace (shown in legend with line style only)
                fig.add_trace(go.Scatter(
                    x=subset['time'],
                    y=subset['surv_time'],
                    mode='lines',  # Only lines for legend
                    name=trace_name,
                    line=dict(color=color, **line_style),
                    hovertemplate=(
                        f'<b>{trace_name}</b><br>'
                        'Time: %{x}<br>'
                        'Survival Rate: %{y:.1f}%<br>'
                        '<extra></extra>'
                    ),
                    showlegend=True  # Show in legend (line only)
                ))
                
                # Add markers separately (hidden from legend)
                fig.add_trace(go.Scatter(
                    x=subset['time'],
                    y=subset['surv_time'],
                    mode='markers',  # Only markers
                    marker=dict(
                        size=marker_size,
                        color=color,
                        symbol=symbol,
                        line=dict(color='white', width=2),  # Thicker white border
                        opacity=0.9
                    ),
                    showlegend=False,  # Hide from legend
                    hoverinfo='skip'  # Skip hover for marker-only trace
                ))
    
    # Calculate the maximum time value from the data for proper X-axis range
    max_time = filtered_df['time'].max() if not filtered_df.empty else 5
    
    # Update layout with enhanced visibility settings
    fig.update_layout(
        title=dict(
            text=f'Survival Curves for {selected_cancer.capitalize()} Cancer',
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Survival time (Years)",
        yaxis_title="Survival rate (%)",
        template='plotly_white',
        autosize=True,
        margin=dict(l=50, r=150, t=80, b=60),  # Responsive margins
        hovermode='closest',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,
            font=dict(size=10),  # Smaller font for mobile
            bordercolor="DarkGray",
            borderwidth=1,
            bgcolor="rgba(255,255,255,0.95)",
            itemsizing="constant",
            itemwidth=30  # Minimum allowed value for Plotly
        ),
        yaxis=dict(
            range=[0, 105],
            title_font=dict(size=12),
            tickfont=dict(size=10),
            ticksuffix='%',
            ticks='inside',
            ticklen=5,
            tickwidth=1,
            linewidth=1,
            linecolor='black',
            automargin=True
        ),
        xaxis=dict(
            range=[0, max_time + 0.5],
            title_font=dict(size=12),
            tickfont=dict(size=10),
            dtick=1,
            ticks='inside',
            ticklen=5,
            tickwidth=1,
            linewidth=1,
            linecolor='black',
            automargin=True
        )
    )
    
    # Add grid for better readability with enhanced visibility
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    
    # Add helpful annotations to explain line styles only
    #if len(selected_regions) > 1:
    #    # Create line style explanation based on number of selected regions
    #    line_explanations = []
    #    line_style_names = ["Solid Line", "Short Dot", "Dot-Medium Dash"]
    #    
    #    for i, region in enumerate(selected_regions):
    #        if i < len(line_style_names):
    #            region_name = f"Region {region}" if region != 'all' else "All Regions"
    #            line_explanations.append(f"• {line_style_names[i]} = {region_name}")
    #    
    #    explanation_text = "📈 Line Styles:<br>" + "<br>".join(line_explanations)
    #    
    #    fig.add_annotation(
    #        text=explanation_text,
    #        xref="paper", yref="paper",
    #        x=0.02, y=0.02,
    #        showarrow=False,
    #        align="left",
    #        xanchor="left",
    #        yanchor="bottom",
    #        borderwidth=2,
    #        bordercolor="darkblue",
    #        bgcolor="rgba(240,248,255,0.95)",
    #        font=dict(size=10, color="darkblue")
    #    )
    
    return fig

if __name__ == "__main__":
    # Example usage
    # Load your data into a DataFrame (df)
    # df = pd.read_csv('your_data.csv')
    pass



