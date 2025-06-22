import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Tuple, Optional

class DataProcessor:
    def __init__(self):
        pass
    
    def format_number(self, value: float, prefix: str = "") -> str:
        """Format numbers with appropriate suffixes"""
        if pd.isna(value) or value is None:
            return "N/A"
        
        if abs(value) >= 1e9:
            return f"{prefix}{value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"{prefix}{value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"{prefix}{value/1e3:.2f}K"
        else:
            return f"{prefix}{value:.2f}"
    
    def format_percentage(self, value: float) -> str:
        """Format percentage with appropriate styling"""
        if pd.isna(value) or value is None:
            return "N/A"
        
        percentage = value * 100
        if percentage > 0:
            return f"+{percentage:.1f}%"
        else:
            return f"{percentage:.1f}%"
    
    def process_financial_statement(self, data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Process financial statement data into DataFrame"""
        try:
            # Extract the actual data - structure may vary
            if isinstance(data, list) and len(data) > 0:
                result_data = data[0].get("result", {}).get("data", {})
            else:
                result_data = data.get("result", {}).get("data", {})
            
            if not result_data:
                return None
            
            # Convert to DataFrame - adapt based on actual structure
            df = pd.DataFrame(result_data)
            return df
        except Exception as e:
            print(f"Error processing financial statement: {e}")
            return None
    
    def process_metrics_breakdown(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process metrics breakdown data"""
        try:
            result = data.get("result", {}).get("data", {}).get("data", [])

            # Loop through the list to find raydium metrics
            for sector in result:
                if sector.get("data_id") == "raydium":
                    return sector.get("metrics", {})
            
            return None
        except Exception as e:
            print(f"Error processing metrics breakdown: {e}")
            return None
    
    def process_time_series(self, data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Process time series data into DataFrame"""
        try:
            result = data.get("result", {}).get("data", {}).get("data", [])
            
            if not result:
                return None
            
            # Extract time series data - adapt based on structure
            df = pd.DataFrame(result)
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            # if 'date' in df.columns:
            #     df['date'] = pd.to_datetime(df['date'])
            #     df = df.sort_values('date')
            
            return df
        except Exception as e:
            print(f"Error processing time series: {e}")
            return None
    
    def create_metric_chart(self, df: pd.DataFrame, metric_name: str, title: str) -> go.Figure:
        """Create a chart for a specific metric"""
        fig = go.Figure()
        
        if df is not None and not df.empty:
            metric_data = df[df['metric_id'] == metric_name]

            if not metric_data.empty and 'timestamp' in metric_data.columns and 'value' in metric_data.columns:
                fig.add_trace(go.Scatter(
                    x=metric_data['timestamp'],
                    y=metric_data['value'],
                    mode='lines+markers',
                    name=metric_name,
                    line=dict(width=3),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title=metric_name.replace('_', ' ').title(),
            template="plotly_dark",
            height=400
        )
        
        return fig
    
    def create_metrics_overview_chart(self, metrics: Dict[str, Any]) -> go.Figure:
        """Create overview chart of key metrics"""
        key_metrics = ['fees', 'revenue', 'trading_volume', 'user_dau', 'tvl']
        
        metric_names = []
        latest_values = []
        changes = []
        
        for metric in key_metrics:
            if metric in metrics:
                metric_data = metrics[metric]
                metric_names.append(metric.replace('_', ' ').title())
                latest_values.append(metric_data.get('latest', 0))
                changes.append(metric_data.get('change', 0) * 100)
        
        fig = go.Figure()
        
        # Create bar chart
        fig.add_trace(go.Bar(
            x=metric_names,
            y=latest_values,
            name='Latest Values',
            marker_color=['green' if change > 0 else 'red' for change in changes]
        ))
        
        fig.update_layout(
            title="Key Metrics Overview",
            template="plotly_dark",
            height=500
        )
        
        return fig