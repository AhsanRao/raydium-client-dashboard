import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Import our custom modules
from config import *
from api_client import TokenTerminalAPI
from data_processor import DataProcessor
from ai_summary import AISummaryGenerator

# Page config
st.set_page_config(
    page_title="Raydium Analytics Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    api_client = TokenTerminalAPI(BEARER_TOKEN, JWT_TOKEN)
    data_processor = DataProcessor()
    ai_generator = AISummaryGenerator(OPENAI_API_KEY)
    return api_client, data_processor, ai_generator

def main():
    st.title("🚀 Raydium Analytics Dashboard")
    
    # Initialize components
    api_client, data_processor, ai_generator = init_components()
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Refresh button
        if st.button("🔄 Refresh All Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Cache settings
        st.subheader("Cache Settings")
        use_cache = st.checkbox("Use cached data", value=True)
        
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")

         # API Data Sources
        st.subheader("📡 Data Sources")
        st.markdown("""
        - 🏢 **Token Terminal** - Financial metrics & DeFi data
        - 🪙 **CoinGecko** - Price & market data
        - 🌊 **DeFiLlama** - TVL & protocol analytics
        
        *Data is aggregated from multiple sources for comprehensive analysis*
        """)
        
        # Last updated
        st.subheader("🕒 Last Updated")
        st.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Load data
    with st.spinner("Loading data..."):
        metrics_data = load_metrics_data(api_client, use_cache)
        financial_data = load_financial_data(api_client, use_cache)
    
    if not metrics_data:
        st.error("❌ Failed to load metrics data. Please check API tokens.")
        return
    
    # AI Summary Section
    st.header("🤖 AI Analysis")
    with st.spinner("Generating AI insights..."):
        ai_summary = ai_generator.generate_summary(metrics_data)
    
    st.info(ai_summary)
    
    # Key Metrics Overview
    st.header("📊 Key Metrics Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if 'revenue' in metrics_data:
            revenue = metrics_data['revenue']['latest']
            revenue_change = metrics_data['revenue']['change']
            st.metric(
                "Revenue", 
                data_processor.format_number(revenue, "$"),
            )
    
    with col2:
        if 'fees' in metrics_data:
            fees = metrics_data['fees']['latest']
            fees_change = metrics_data['fees']['change']
            st.metric(
                "Fees", 
                data_processor.format_number(fees, "$"),
            )
    
    with col3:
        if 'trading_volume' in metrics_data:
            volume = metrics_data['trading_volume']['latest']
            volume_change = metrics_data['trading_volume']['change']
            st.metric(
                "Trading Volume", 
                data_processor.format_number(volume, "$"),
            )
    
    with col4:
        if 'user_mau' in metrics_data:
            mau = metrics_data['user_mau']['latest']
            mau_change = metrics_data['user_mau']['change']
            st.metric(
                "Monthly Users", 
                data_processor.format_number(mau),
            )
    
    with col5:
        if 'tvl' in metrics_data:
            tvl = metrics_data['tvl']['latest']
            tvl_change = metrics_data['tvl']['change']
            st.metric(
                "TVL", 
                data_processor.format_number(tvl, "$"),
                # data_processor.format_percentage(tvl_change) + " (30d change)" if tvl_change is not None else ""
            )
    
    # Advanced Analytics Section
    st.header("📊 Advanced Analytics")

    # Pie Charts Row
    st.subheader("📈 Breakdown Analysis")
    pie_col1, pie_col2 = st.columns(2)

    with pie_col1:
        if metrics_data:
            revenue_fees_pie = data_processor.create_revenue_fees_pie(metrics_data)
            st.plotly_chart(revenue_fees_pie, use_container_width=True)

    with pie_col2:
        if metrics_data:
            user_engagement_pie = data_processor.create_user_engagement_pie(metrics_data)
            st.plotly_chart(user_engagement_pie, use_container_width=True)

    # Stacked Bar Charts
    st.subheader("📊 Trend Analysis")

    stacked_col1, stacked_col2 = st.columns(2)

    with stacked_col1:
        with st.spinner("Loading revenue & fees trend..."):
            revenue_fees_stacked = data_processor.create_revenue_fees_stacked_bar(api_client, use_cache)
            st.plotly_chart(revenue_fees_stacked, use_container_width=True)

    with stacked_col2:
        with st.spinner("Loading user growth patterns..."):
            user_growth_stacked = data_processor.create_user_growth_stacked_bar(api_client, use_cache)
            st.plotly_chart(user_growth_stacked, use_container_width=True)

    # Volume breakdown (full width)
    with st.spinner("Loading volume breakdown..."):
        volume_breakdown = data_processor.create_volume_breakdown_stacked_bar(api_client, use_cache)
        st.plotly_chart(volume_breakdown, use_container_width=True)
    # Detailed Metrics Table
    st.header("📋 Detailed Metrics")
    
    if metrics_data:
        metrics_df = create_metrics_table(metrics_data, data_processor)
        st.dataframe(metrics_df, use_container_width=True)
    
    # Charts Section
    st.header("📈 Time Series Charts")
    
    # Chart selection
    available_metrics = [
        'fees', 'revenue', 'trading_volume', 'user_dau', 'user_mau', 
        'tvl', 'price', 'active_developers', 'token_trading_volume'
    ]
    
    selected_metrics = st.multiselect(
        "Select metrics to visualize:",
        available_metrics,
        default=['fees', 'revenue', 'trading_volume', 'user_mau']
    )
    
    # Create charts
    chart_cols = st.columns(2)
    
    for i, metric in enumerate(selected_metrics):
        with chart_cols[i % 2]:
            with st.spinner(f"Loading {metric} chart..."):
                chart_data = load_time_series_data(api_client, metric, use_cache)
                if chart_data is not None and not chart_data.empty:
                    fig = data_processor.create_metric_chart(
                        chart_data, 
                        metric, 
                        f"{metric.replace('_', ' ').title()} Over Time"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for {metric}")
    
    # Financial Statement
    financial_data, operational_data = load_financial_data(api_client, use_cache)

    if financial_data is not None and not financial_data.empty:
        st.header("💰 Financial Statement")
        st.dataframe(
            financial_data, 
            use_container_width=True,
            height=400,
            column_config={
                col: st.column_config.TextColumn(col, width="medium") 
                for col in financial_data.columns
            }
        )
    else:
        st.header("💰 Financial Statement")
        st.info("No financial data available.")

    if operational_data is not None and not operational_data.empty:
        st.header("📊 Operational Metrics")
        st.dataframe(
            operational_data, 
            use_container_width=True,
            height=400,
            column_config={
                col: st.column_config.TextColumn(col, width="medium") 
                for col in operational_data.columns
            }
        )
    else:
        st.header("📊 Operational Metrics")
        st.info("No operational data available.")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_metrics_data(_api_client, use_cache=True):
    """Load and cache metrics breakdown data"""
    data = _api_client.get_metrics_breakdown(use_cache=use_cache)

    if data:
        processor = DataProcessor()
        return processor.process_metrics_breakdown(data)
    return None

@st.cache_data(ttl=3600)
def load_financial_data(_api_client, use_cache=True):
    """Load and cache financial statement data"""
    data = _api_client.get_financial_statement(use_cache=use_cache)
    
    if data:
        processor = DataProcessor()
        return processor.process_financial_statement(data)
    return None

@st.cache_data(ttl=3600)
def load_time_series_data(_api_client, metric_id, use_cache=True):
    """Load and cache time series data for a specific metric"""
    data = _api_client.get_time_series(metric_id, use_cache=use_cache)
    if data:
        processor = DataProcessor()
        return processor.process_time_series(data)
    return None

def create_metrics_table(metrics_data, data_processor):
    """Create formatted metrics table"""
    rows = []
    
    for metric_name, metric_data in metrics_data.items():
        if isinstance(metric_data, dict):
            change = metric_data.get('change', 0)
            change_str = data_processor.format_percentage(change)
            if change > 0:
                change_str += ' ▲'
            elif change < 0:
                change_str += ' ▼'
            else:
                change_str += ' →'

            rows.append({
                'Metric': metric_name.replace('_', ' ').title(),
                'Latest Value': data_processor.format_number(metric_data.get('latest', 0)),
                'Change (30d %)': change_str,
                'Average': data_processor.format_number(metric_data.get('avg', 0)),
            })
    
    return pd.DataFrame(rows)

if __name__ == "__main__":
    main()
