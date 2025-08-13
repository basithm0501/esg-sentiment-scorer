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

# Company selection
company_name = st.sidebar.text_input("Company Name", value="Apple Inc.")
ticker_symbol = st.sidebar.text_input("Ticker Symbol (Optional)", value="AAPL")

# Time period selection
time_period = st.sidebar.selectbox(
    "Analysis Period",
    ["1d", "7d", "30d", "90d", "1y"],
    index=2
)

# Sector selection
sector = st.sidebar.selectbox(
    "Sector",
    ["Technology", "Healthcare", "Financial", "Energy", "Consumer", "Industrial", "Other"],
    index=0
)

# Analysis button
analyze_button = st.sidebar.button("🚀 Analyze Company", type="primary")

# Main content area
if analyze_button or company_name:
    
    # Mock data for demonstration
    # TODO: Replace with actual API calls
    
    # ESG Scores
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌱 Environmental", "0.75", "0.05")
    with col2:
        st.metric("👥 Social", "0.68", "-0.02")
    with col3:
        st.metric("🏛️ Governance", "0.82", "0.08")
    with col4:
        st.metric("📊 Overall ESG", "0.75", "0.04")
    
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

else:
    # Welcome screen
    st.info("👆 Enter a company name in the sidebar to begin ESG analysis")
    
    # Sample companies
    st.subheader("🏢 Try analyzing these companies:")
    
    sample_companies = [
        ("Apple Inc.", "AAPL", "Technology"),
        ("Microsoft", "MSFT", "Technology"), 
        ("Tesla", "TSLA", "Automotive"),
        ("Johnson & Johnson", "JNJ", "Healthcare"),
        ("JPMorgan Chase", "JPM", "Financial")
    ]
    
    cols = st.columns(3)
    for i, (name, ticker, sector) in enumerate(sample_companies):
        with cols[i % 3]:
            if st.button(f"{name} ({ticker})"):
                st.experimental_set_query_params(company=name, ticker=ticker)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>ESG Sentiment Scorer v1.0.0 | Built with ❤️ for sustainable investing</p>
    <p><em>Disclaimer: This tool is for educational and research purposes. 
    Investment decisions should involve professional financial advice.</em></p>
</div>
""", unsafe_allow_html=True)
