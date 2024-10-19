import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from sklearn.linear_model import LinearRegression

# Load Data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Custom CSS
st.markdown("""
    <style>
        .title {
            font-size: 40px;
            color: #007A78;
            text-align: center;
        }
        .description {
            font-size: 18px;
            margin-bottom: 20px;
            color: #333;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 12px;
            color: #777;
        }
        .input-label {
            font-weight: bold;
        }
        .section-title {
            font-size: 24px;
            color: #007A78;
            margin-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# App Title and Description
st.markdown('<div class="title">🏠 HDB PricePulse</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Introducing HDB PricePulse, your go-to tool for accurate HDB resale price estimates and market trends. Input key details and get instant price predictions based on real-time data. Track and visualize market trends to stay ahead in your property decisions!</div>', unsafe_allow_html=True)

# Sidebar for User Input
st.sidebar.header("User Input")
town = st.sidebar.selectbox('Town', ['ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH',
                                      'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG',
                                      'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST',
                                      'KALLANG/WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL',
                                      'QUEENSTOWN', 'SEMBAWANG', 'SENGKANG', 'SERANGOON', 'TAMPINES',
                                      'TOA PAYOH', 'WOODLANDS', 'YISHUN'])

flat_type = st.sidebar.selectbox('Flat Type', ['1 ROOM', '2 ROOM', '3 ROOM', '4 ROOM', '5 ROOM', 
                                                'EXECUTIVE', 'MULTI-GENERATION'])

storey_range = st.sidebar.selectbox('Storey Range', ['01 TO 03', '04 TO 06', '07 TO 09', '10 TO 12', 
                                                      '13 TO 15', '16 TO 18', '19 TO 21', '22 TO 24', 
                                                      '25 TO 27', '28 TO 30', '31 TO 33', '34 TO 36', 
                                                      '37 TO 39', '40 TO 42', '43 TO 45', '46 TO 48', 
                                                      '49 TO 51'])

floor_area_sqm = st.sidebar.number_input('Floor Area (sqm)', min_value=0) 
remaining_lease_years = st.sidebar.number_input('Remaining Lease Years', min_value=0)                                             

# Load data
with st.spinner("Loading data..."):
    df = load_data("Resale_Dataset.csv")

# Train a simple linear regression model
features = ['town', 'flat_type', 'storey_range', 'floor_area_sqm', 'year', 'month_of_year', 'remaining_lease_years']
X = df[features]
y = df['resale_price']

# Encode categorical features
X = pd.get_dummies(X, columns=['town', 'flat_type', 'storey_range'], drop_first=True)

# Fit the linear regression model
model = LinearRegression()
model.fit(X, y)

# Prediction
if st.sidebar.button('Predict'):
    # Pre-process user input
    month_of_year = datetime.now().month
    year = datetime.now().year

    town_dict = {town: idx for idx, town in enumerate(df['town'].unique())}
    flat_type_dict = {flat_type: idx for idx, flat_type in enumerate(df['flat_type'].unique())}
    storey_range_dict = {storey_range: idx for idx, storey_range in enumerate(df['storey_range'].unique())}

    input_data = pd.DataFrame({
        'town': [town_dict[town]],
        'flat_type': [flat_type_dict[flat_type]],
        'storey_range': [storey_range_dict[storey_range]],
        'floor_area_sqm': [floor_area_sqm], 
        'year': [year],
        'month_of_year': [month_of_year],
        'remaining_lease_years': [remaining_lease_years]
    })

    input_data_encoded = pd.get_dummies(input_data, columns=['town', 'flat_type', 'storey_range'], drop_first=True)
    missing_cols = set(X.columns) - set(input_data_encoded.columns)
    for col in missing_cols:
        input_data_encoded[col] = 0
    input_data_encoded = input_data_encoded[X.columns]

    prediction = model.predict(input_data_encoded)
    st.success(f'Resale Price Prediction: ${prediction[0]:,.2f}')

# Market Trend Section
st.markdown('<div class="section-title">📈 Market Trend</div>', unsafe_allow_html=True)

avg_price_by_year = df.groupby('year')['resale_price'].mean().reset_index()
fig = go.Figure(data=[go.Scatter(x=avg_price_by_year['year'], 
                                   y=avg_price_by_year['resale_price'], 
                                   mode='lines+markers',
                                   marker=dict(color='blue'),
                                   hovertemplate='Year: %{x}<br>Average Resale Price: %{y:,.0f}<extra></extra>')])
fig.update_layout(title='Resale Price Trend Across Years',
                  xaxis_title='Year',
                  yaxis_title='Average Resale Price',
                  template='plotly_dark')
st.plotly_chart(fig)

# Average Resale Price by Flat Type
st.markdown('<div class="section-title">📊 Average Resale Price by Flat Type in 2024</div>', unsafe_allow_html=True)
df_2024 = df[df['year'] == 2024]
avg_price_by_flat_type = df_2024.groupby('flat_type')['resale_price'].mean().reset_index()
fig = go.Figure(data=[go.Bar(x=avg_price_by_flat_type['flat_type'], 
                              y=avg_price_by_flat_type['resale_price'],
                              marker=dict(color='#FFC745'))])
fig.update_layout(title='Average Resale Price by Flat Type in 2024',
                  xaxis_title='Flat Type',
                  yaxis_title='Average Resale Price')
st.plotly_chart(fig)

# Average Resale Price by Town
st.markdown('<div class="section-title">🏘️ Average Resale Price by Town in 2024</div>', unsafe_allow_html=True)
avg_price_by_town = df_2024.groupby('town')['resale_price'].mean().reset_index()
avg_price_by_town = avg_price_by_town.sort_values(by='resale_price', ascending=False)
fig = go.Figure(data=[go.Bar(x=avg_price_by_town['town'], 
                              y=avg_price_by_town['resale_price'],
                              marker=dict(color='#007A78'))])
fig.update_layout(title='Average Resale Price by Town in 2024',
                  xaxis_title='Town',
                  yaxis_title='Average Resale Price')
st.plotly_chart(fig)

# Footer
st.markdown('<div class="footer">© 2024 HDB PricePulse | [Contact Us](mailto:your_email@example.com)</div>', unsafe_allow_html=True)
