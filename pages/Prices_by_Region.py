import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
import logging
from helper_functions.utility import check_password  # Import the check_password function

# Add custom CSS
st.markdown("""
    <style>

        h1 {
            color: #2c3e50;
        }
        h2 {
            color: #2980b9;
        }
        .stButton>button {
            background-color: #27ae60;
            color: white;
        }
        .stButton>button:hover {
            background-color: #219653;
        }
        .chart-container {
            margin-top: 20px;
        }
        .description {
            font-size: 18px;
            color: #34495e;
        }
    </style>
""", unsafe_allow_html=True)



# Set the title of the Streamlit app
st.markdown('<div class="main">', unsafe_allow_html=True)
st.title("HDB Prices by Region")

# Description
st.markdown('<div class="description">', unsafe_allow_html=True)
st.write(""" 
select the town of your choice for average pricing.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Define the path to your CSV file
csv_file_path = "Resale_Dataset.csv"

@st.cache_data
def load_data(file_path):
    """Loads data from the given CSV file and returns it as a Pandas DataFrame."""
    df = pd.read_csv(file_path)
    return df

# Fetch the data from CSV
with st.spinner("Loading data..."):
    df = load_data(csv_file_path)

# Formatting Fields
df['remaining_lease_years'] = df['remaining_lease'].str.extract(r'(\d+)').astype(float)
df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
df['year'] = df['month'].dt.year
df['month_of_year'] = df['month'].dt.month
df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
df = df.dropna(subset=['resale_price', 'remaining_lease_years', 'town', 'flat_type', 'storey_range', 'floor_area_sqm'])

#################################################################################
# Subheader for Market Trend
st.subheader("Market Trend")

# Group by year and calculate the average resale price
avg_price_by_year = df.groupby('year')['resale_price'].mean().reset_index()

# Create a line chart using Plotly for better customization
# Create the line chart using Matplotlib
# Create a Plotly figure
import plotly.graph_objects as go

# Create a Plotly figure
# Create the line chart using Matplotlib
# Create a Plotly figure
import streamlit as st
import plotly.graph_objects as go

# Create a Plotly figure
fig = go.Figure(data=[go.Scatter(x=avg_price_by_year['year'], y=avg_price_by_year['resale_price'], mode='lines+markers', marker=dict(color='blue'),
                                 text=avg_price_by_year['resale_price'],  # Add text for labels
                                 hovertemplate='Year: %{x}<br>Average Resale Price: %{y:,.0f}<extra></extra>')])  # Customize hover tooltip

# Update layout (optional)
fig.update_layout(
    title='Resale Price Trend Across Years',
    xaxis_title='Year',
    yaxis_title='Average Resale Price',
    template='plotly_dark'  # Optional: Choose a different template for styling
)

# Display the plot using st.plotly_chart
st.plotly_chart(fig)

# Flat Type Comparison:

# Filter for 2024 data
df_2024 = df[df['year'] == 2024]

# Group by flat type and calculate average resale price
avg_price_by_flat_type = df_2024.groupby('flat_type')['resale_price'].mean().reset_index()

# Create a bar chart
fig = go.Figure(data=[go.Bar(x=avg_price_by_flat_type['flat_type'], y=avg_price_by_flat_type['resale_price'],marker=dict(color='#FFC745'))])
fig.update_layout(title='Average Resale Price by Flat Type in 2024', xaxis_title='Flat Type', yaxis_title='Average Resale Price')
st.plotly_chart(fig)

#Location:
# Group by town and calculate average resale price
avg_price_by_town = df_2024.groupby('town')['resale_price'].mean().reset_index()

# Sort towns by resale price (descending)
avg_price_by_town = avg_price_by_town.sort_values(by='resale_price', ascending=False)

# Create a bar chart
fig = go.Figure(data=[go.Bar(x=avg_price_by_town['town'], y=avg_price_by_town['resale_price'],marker=dict(color='#007A78'))])
fig.update_layout(title='Average Resale Price by Town in 2024', xaxis_title='Town', yaxis_title='Average Resale Price')
st.plotly_chart(fig)



