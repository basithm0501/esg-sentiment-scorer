"""
Streamlit Dashboard for ESG Sentiment Scorer
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

# Page configuration
st.set_page_config(
    page_title="ESG Sentiment Scorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .esg-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🌍 ESG Sentiment Scorer</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered ESG analysis for investment decision making**")

# Sidebar
st.sidebar.header("🔍 Analysis Configuration")

# Load ESG scores and risk metrics
esg_scores_path = "data/processed/company_esg_scores.csv"
esg_risk_path = "data/processed/company_esg_risk_scores.csv"

esg_scores_df = pd.read_csv(esg_scores_path)
esg_risk_df = pd.read_csv(esg_risk_path)

# Company selection from real data
company_options = esg_scores_df["company"].unique().tolist()
company_name = st.sidebar.selectbox("Company Name", company_options, index=0)

# Get scores for selected company
selected_scores = esg_scores_df[esg_scores_df["company"] == company_name].iloc[0]
selected_risk = esg_risk_df[esg_risk_df["company"] == company_name].iloc[0]

# ESG Scores
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌱 Environmental", f"{selected_scores['environment_score']:.2f}", f"Risk: {selected_risk['environment_risk']:.0f}")
with col2:
    st.metric("👥 Social", f"{selected_scores['social_score']:.2f}", f"Risk: {selected_risk['social_risk']:.0f}")
with col3:
    st.metric("🏛️ Governance", f"{selected_scores['governance_score']:.2f}", f"Risk: {selected_risk['governance_risk']:.0f}")
with col4:
    st.metric("📊 Overall ESG", f"{selected_scores[['environment_score','social_score','governance_score']].mean():.2f}", f"Risk: {selected_risk['overall_risk']:.0f}")

# ESG Score Visualization
st.subheader("📈 ESG Score Breakdown")

col1, col2 = st.columns([2, 1])

with col1:
    # Radar chart for ESG scores
    categories = ['Environmental', 'Social', 'Governance', 'Transparency', 'Innovation']
    scores = [0.75, 0.68, 0.82, 0.72, 0.79]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name=company_name,
        line_color='rgba(46, 139, 87, 0.8)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="ESG Performance Radar"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    # ESG Score gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=0.75,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall ESG Score"},
        delta={'reference': 0.70},
        gauge={
            'axis': {'range': [None, 1]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 0.5], 'color': "lightgray"},
                {'range': [0.5, 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        }
    ))

    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# Recent News Analysis
st.subheader("📰 Recent News Sentiment")

# Mock news data
news_data = pd.DataFrame({
    'Date': pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D'),
    'Sentiment': np.random.normal(0.1, 0.3, 31),
    'Volume': np.random.poisson(5, 31)
})

col1, col2 = st.columns(2)

with col1:
    # Sentiment timeline
    fig = px.line(news_data, x='Date', y='Sentiment', 
                 title="News Sentiment Over Time",
                 labels={'Sentiment': 'Sentiment Score'})
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # News volume
    fig = px.bar(news_data.tail(10), x='Date', y='Volume',
                title="Recent News Volume",
                labels={'Volume': 'Number of Articles'})
    st.plotly_chart(fig, use_container_width=True)

# Risk Assessment
st.subheader("⚠️ Risk Assessment")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 Low Risk Factors")
    st.write("- Strong governance practices")
    st.write("- Consistent ESG reporting")
    st.write("- Positive environmental initiatives")

with col2:
    st.markdown("### 🟡 Medium Risk Factors")
    st.write("- Social media sentiment volatility")
    st.write("- Regulatory compliance monitoring")
    st.write("- Supply chain transparency")

with col3:
    st.markdown("### 🔴 High Risk Factors")
    st.write("- None identified currently")
    st.write("- Monitor for regulatory changes")
    st.write("- Watch competitive pressures")

# Investment Recommendation
st.subheader("💼 Investment Recommendation")

recommendation_col1, recommendation_col2 = st.columns([2, 1])

with recommendation_col1:
    st.success("""
    **HOLD with Positive ESG Outlook** 📈

    Based on the comprehensive ESG analysis, this company demonstrates:
    - Strong governance framework (0.82/1.0)
    - Improving environmental initiatives (0.75/1.0) 
    - Stable social responsibility practices (0.68/1.0)

    **Key Strengths:**
    - Consistent ESG disclosure and transparency
    - Active environmental sustainability programs
    - Strong corporate governance structure

    **Areas for Monitoring:**
    - Social impact initiatives could be strengthened
    - Watch for regulatory changes in the sector
    - Monitor competitive ESG performance
    """)

with recommendation_col2:
    # Risk level indicator
    risk_level = "Medium-Low"
    risk_color = "green"

    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #f0f8f0; border-radius: 10px;">
        <h3 style="color: {risk_color};">Risk Level</h3>
        <h2 style="color: {risk_color};">{risk_level}</h2>
        <p>Confidence: 85%</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>ESG Sentiment Scorer v1.0.0 | Built with ❤️ for sustainable investing</p>
    <p><em>Disclaimer: This tool is for educational and research purposes. 
    Investment decisions should involve professional financial advice.</em></p>
</div>
""", unsafe_allow_html=True)
