import streamlit as st
import pandas as pd
import logging
import plotly.graph_objects as go

# Add custom CSS
st.markdown("""
    <style>
        h1 { color: #2c3e50; }
        h2 { color: #2980b9; }
        .stButton>button { background-color: #27ae60; color: white; }
        .stButton>button:hover { background-color: #219653; }
        .chart-container { margin-top: 20px; }
        .description { font-size: 18px; color: #34495e; }
    </style>
""", unsafe_allow_html=True)

# Set the title of the Streamlit app
st.title("HDB Prices by Region")

# Description
st.write("Select the year and flat type of your choice for average pricing.")

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
df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
df = df.dropna(subset=['resale_price', 'remaining_lease_years', 'town', 'flat_type', 'storey_range', 'floor_area_sqm'])

# Year and Flat Type Dropdowns
years = df['year'].unique()
flat_types = df['flat_type'].unique()

selected_year = st.selectbox("Select Year", years)
selected_flat_type = st.selectbox("Select Flat Type", flat_types)

# Filter data based on selections
filtered_data = df[(df['year'] == selected_year) & (df['flat_type'] == selected_flat_type)]

# Market Trend
st.subheader("Market Trend")

# Group by town and calculate average resale price
avg_price_by_town = filtered_data.groupby('town')['resale_price'].mean().reset_index()

# Sort towns by resale price (descending)
avg_price_by_town = avg_price_by_town.sort_values(by='resale_price', ascending=False)

# Create a gradient color scale based on resale price
colors = [
    f'rgba(0, {int(255 * (i / len(avg_price_by_town)))}, 120, 0.8)' 
    for i in range(len(avg_price_by_town))
]

# Create a bar chart with gradient colors
