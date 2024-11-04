import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
Select the town of your choice for average pricing.
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
df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
df = df.dropna(subset=['resale_price', 'remaining_lease_years', 'town'])

# Subheader for Market Trend
st.subheader("Market Trend")

# Filter for 2023 data
df_2023 = df[df['year'] == 2023]

# Group by town and calculate average resale price
avg_price_by_town = df_2023.groupby('town')['resale_price'].mean().reset_index()

# Sort towns by resale price (descending)
avg_price_by_town = avg_price_by_town.sort_values(by='resale_price', ascending=False)

# Example town coordinates (latitude and longitude)
town_coordinates = {
    'Town1': (1.290270, 103.851959),  # Example coordinates
    'Town2': (1.305256, 103.819499),
    'Town3': (1.366066, 103.828690),
    # Add all towns with their respective coordinates
}

# Add latitude and longitude to the DataFrame
avg_price_by_town['latitude'] = avg_price_by_town['town'].map(lambda town: town_coordinates.get(town, (None, None))[0])
avg_price_by_town['longitude'] = avg_price_by_town['town'].map(lambda town: town_coordinates.get(town, (None, None))[1])

# Dropdown for selecting town
selected_town = st.selectbox("Select a Town:", options=avg_price_by_town['town'].unique())

# Filter data based on selected town
filtered_data = avg_price_by_town[avg_price_by_town['town'] == selected_town]

# Create a map for the selected town
if not filtered_data.empty:
    fig = go.Figure(go.Scattermapbox(
        mode='markers+text',
        lat=filtered_data['latitude'],
        lon=filtered_data['longitude'],
        text=filtered_data['town'] + "<br>Avg Resale Price: $" + filtered_data['resale_price'].astype(str),
        marker=dict(size=14, color='#007A78', opacity=0.7),
    ))

    fig.update_layout(
        title=f'Average Resale Price for {selected_town} in 2023',
        mapbox=dict(
            style='carto-positron',
            center=dict(lat=filtered_data['latitude'].values[0], lon=filtered_data['longitude'].values[0]),
            zoom=12
        ),
        showlegend=False
    )

    st.plotly_chart(fig)
else:
    st.warning("No data available for the selected town.")
