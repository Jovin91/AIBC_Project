import streamlit as st

# Title with a suitable logo
st.markdown("# **About Us**")

# Create an expander for the disclaimer
with st.expander("IMPORTANT NOTICE: Click to expand/disclose", expanded=False):
    st.write("""
    This web application is a prototype developed for educational purposes only. 
    The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, 
    especially those related to financial, legal, or healthcare matters.

    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
    You assume full responsibility for how you use any generated output.

    Always consult with qualified professionals for accurate and personalized advice.
    """)

# Project Scope with Icon
st.markdown("### **Modules**")
st.markdown("""
The Topic is on HDB resale and it comprises two main modules:

1. **How_to_Resale**: A chatbot that helps you look through the HDB website and other sources on processes and requirements for Resale HDB.
2. **HDB prices by region**: A trending of the average resale prices by region based on 2023.
""")

# Data Sources with Icon
st.markdown("### **Data Sources**")
st.markdown("""
Information on requirements and processes are extracted from these websites, including HDB official website and other useful website such as My Money sense and dollars and sense:

1. **URLs Scraped**: 
  - [Considerations when deciding to buy a resale](https://www.mymoneysense.gov.sg/buying-a-house/purchase-guide/new-or-resale-flat)
  - [Step-by-step guide to buying a resale flat] (https://dollarsandsense.sg/step-step-guide-buying-resale-hdb-flat-singapore/)
  - [Overview of Buying Procedure](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/overview)
  - [HDB Flat Eligibility Letter (HFE)](https://www.hdb.gov.sg/residential/buying-a-flat/understanding-your-eligibility-and-housing-loan-options/application-for-an-hdb-flat-eligibility-hfe-letter)
  - [Plan, Source, and Contract](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract)
  - [Planning Considerations](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/planning-considerations)
  - [Mode of Financing](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/mode-of-financing)
  - [Grants for resale flats](https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/understanding-your-eligibility-and-housing-loan-options/flat-and-grant-eligibility/couples-and-families/cpf-housing-grants-for-resale-flats-families)
  - [Option to Purchase](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/option-to-purchase)
  - [Request for Value](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/plan-source-and-contract/request-for-value)
  - [Resale Application](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/resale-application/application)
  - [Acceptance and Approval](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/resale-application/acceptance-and-approval)
  - [Resale Completion](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-resale-flats/resale-completion)
  - [Conditions After Buying](https://www.hdb.gov.sg/residential/buying-a-flat/conditions-after-buying)

2. **Resale Dataset**: A comprehensive CSV dataset containing historical resale prices, flat types, town locations, and other pertinent features essential for training our predictive models.
- **Dataset Source**: Downloaded from [Data.gov.sg](https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view) and hosted locally.
""")

if __name__ == "__main__":
    # Removed the unwanted section
    pass
