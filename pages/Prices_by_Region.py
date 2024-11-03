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

# Filter for 2024 data
df_2023 = df[df['year'] == 2023]

#Location:
# Group by town and calculate average resale price
avg_price_by_town = df_2023.groupby('town')['resale_price'].mean().reset_index()

# Sort towns by resale price (descending)
avg_price_by_town = avg_price_by_town.sort_values(by='resale_price', ascending=False)

# Create a bar chart
fig = go.Figure(data=[go.Bar(x=avg_price_by_town['town'], y=avg_price_by_town['resale_price'],marker=dict(color='#007A78'))])
fig.update_layout(title='Average Resale Price by Town in 2023', xaxis_title='Town', yaxis_title='Average Resale Price')
st.plotly_chart(fig)



