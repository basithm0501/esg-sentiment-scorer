import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="ESG Investment Risk Dashboard", layout="wide")
st.title("ESG Investment Risk Dashboard")

# Load risk scores
risk_df = pd.read_csv("data/processed/company_esg_risk_scores.csv")

# Example sector/region mapping (replace with your real data if available)
sector_map = {
    "Apple Inc.": "Technology", "Morgan Stanley": "Finance", "Alphabet Inc.": "Technology",
    "Sony Group": "Technology", "SAP SE": "Technology", "JPMorgan Chase": "Finance",
    "Goldman Sachs": "Finance", "Bank of America": "Finance", "Santander": "Finance",
    "UBS Group": "Finance", "Mizuho Financial": "Finance", "Novartis AG": "Healthcare",
    "Coca-Cola Company": "Consumer", "Nestle SA": "Consumer", "General Electric": "Industrial",
    "Caterpillar Inc.": "Industrial", "Bank of China": "Finance", "Meta Platforms": "Technology"
}
region_map = {
    "Apple Inc.": "Americas", "Morgan Stanley": "Americas", "Alphabet Inc.": "Americas",
    "Sony Group": "Asia", "SAP SE": "Europe", "JPMorgan Chase": "Americas",
    "Goldman Sachs": "Americas", "Bank of America": "Americas", "Santander": "Europe",
    "UBS Group": "Europe", "Mizuho Financial": "Asia", "Novartis AG": "Europe",
    "Coca-Cola Company": "Americas", "Nestle SA": "Europe", "General Electric": "Americas",
    "Caterpillar Inc.": "Americas", "Bank of China": "Asia", "Meta Platforms": "Americas"
}
risk_df["sector"] = risk_df["company"].map(sector_map)
risk_df["region"] = risk_df["company"].map(region_map)

st.sidebar.header("Filters")
selected_sector = st.sidebar.multiselect("Sector", sorted(risk_df["sector"].dropna().unique()), default=None)
selected_region = st.sidebar.multiselect("Region", sorted(risk_df["region"].dropna().unique()), default=None)

filtered_df = risk_df.copy()
if selected_sector:
    filtered_df = filtered_df[filtered_df["sector"].isin(selected_sector)]
if selected_region:
    filtered_df = filtered_df[filtered_df["region"].isin(selected_region)]

st.subheader("ESG Risk Heatmap by Sector")
heatmap_sector = filtered_df.pivot_table(index="company", columns="sector", values="overall_risk")
fig_sector = px.imshow(heatmap_sector, color_continuous_scale="RdYlGn_r", aspect="auto", labels=dict(color="Risk (0=Low, 100=High)"))
st.plotly_chart(fig_sector, use_container_width=True)

st.subheader("ESG Risk Heatmap by Region")
heatmap_region = filtered_df.pivot_table(index="company", columns="region", values="overall_risk")
fig_region = px.imshow(heatmap_region, color_continuous_scale="RdYlGn_r", aspect="auto", labels=dict(color="Risk (0=Low, 100=High)"))
st.plotly_chart(fig_region, use_container_width=True)

st.dataframe(filtered_df)
