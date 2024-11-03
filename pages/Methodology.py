import streamlit as st

# Set the title of the Streamlit app
st.title("Methodology")

# Section for HDB Price Pulse
st.markdown("### **Prices by Region**")

# Add space using HTML line break
st.markdown("<br>", unsafe_allow_html=True)

# Insert Image 1
st.image("Images/Flow Chart 1.png", caption="Flow Chart 1", use_column_width=True)

# Section for Ask Our Resale Genie
st.markdown("### 🧞 **How to Resale**")

# Add space using HTML line break
st.markdown("<br>", unsafe_allow_html=True)

# Insert Image 2
st.image("Images/Flow Chart 2.png", caption="Flow Chart 2", use_column_width=True)
