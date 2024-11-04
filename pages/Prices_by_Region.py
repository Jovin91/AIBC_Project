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
df = df.dropna(subset=['resale_price', 'remaining_lease_years', 'town', 'flat_type'])

# Year and Flat Type Dropdowns
years = df['year'].unique()
flat_types = df['flat_type'].unique()

selected_year = st.selectbox("Select Year", years)
selected_flat_type = st.selectbox("Select Flat Type", flat_types)

# Budget Input
budget = st.number_input("Enter your budget (in SGD)", min_value=0, value=500000, step=10000)

# Filter data based on selections
filtered_data = df[(df['year'] == selected_year) & (df['flat_type'] == selected_flat_type)]

# Check if filtered data is empty
if filtered_data.empty:
    st.warning("No data available for the selected year and flat type.")
else:
    # Market Trend
    st.subheader("Market Trend")

    # Group by town and calculate average resale price
    avg_price_by_town = filtered_data.groupby('town')['resale_price'].mean().reset_index()

    # Filter towns within the budget
    avg_price_by_town = avg_price_by_town[avg_price_by_town['resale_price'] <= budget]

    # Check if there are towns within the budget
    if avg_price_by_town.empty:
        st.warning("No towns available within your budget.")
    else:
        # Sort towns by resale price (descending)
        avg_price_by_town = avg_price_by_town.sort_values(by='resale_price', ascending=False)

        # Create a simple color list (for now, we'll just use a gradient from blue to green)
        colors = [f'rgba(0, {int(255 * (price / avg_price_by_town["resale_price"].max()))}, 255, 1)' for price in avg_price_by_town['resale_price']]

        # Create a bar chart
        fig = go.Figure(data=[go.Bar(
            x=avg_price_by_town['town'],
            y=avg_price_by_town['resale_price'],
            marker=dict(color=colors)
        )])

        # Update layout
        fig.update_layout(
            title='Average Resale Price by Town',
            xaxis_title='Town',
            yaxis_title='Average Resale Price',
            showlegend=False
        )

        # Add house icons as annotations (optional)
        for index, row in avg_price_by_town.iterrows():
            fig.add_annotation(
                x=row['town'],
                y=row['resale_price'],
                text='🏠',  # Unicode house emoji
                showarrow=False,
                font=dict(size=20)
            )

        st.plotly_chart(fig)
