import streamlit as st
import pandas as pd
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
st.title("HDB Prices by Region")

# Description
st.write("Select the town and flat type of your choice for average pricing.")

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

# Subheader for Market Trend
st.subheader("Market Trend")

# Dropdown for selecting year
years = df['year'].unique()
selected_year = st.selectbox("Select a Year:", options=sorted(years))

# Filter for selected year
df_selected_year = df[df['year'] == selected_year]

# Dropdown for selecting town
towns = df_selected_year['town'].unique()
selected_town = st.selectbox("Select a Town:", options=sorted(towns))

# Filter data for the selected town
df_town = df_selected_year[df_selected_year['town'] == selected_town]

# Dropdown for selecting flat type
flat_types = df_town['flat_type'].unique()
selected_flat_type = st.selectbox("Select a Flat Type:", options=sorted(flat_types))

# Filter data for the selected flat type
filtered_data = df_town[df_town['flat_type'] == selected_flat_type]

# Group by town and calculate average resale price for the selected year and flat type
avg_price_by_town = filtered_data.groupby('town')['resale_price'].mean().reset_index()

# Create a bar chart for the selected town and flat type
if not avg_price_by_town.empty:
    fig = go.Figure(data=[
        go.Bar(x=avg_price_by_town['town'], y=avg_price_by_town['resale_price'], marker=dict(color='#007A78'))
    ])
    fig.update_layout(title=f'Average Resale Price for {selected_flat_type} in {selected_town} for {selected_year}',
                      xaxis_title='Town', yaxis_title='Average Resale Price',
                      yaxis_tickprefix="$", showlegend=False)
    st.plotly_chart(fig)
else:
    st.warning("No data available for the selected filters.")
