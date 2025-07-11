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
    
    def process_financial_statement(self, data: Dict[str, Any]) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Process financial statement data into two formatted tables: financial and operational metrics"""
        try:
            # Extract the actual data - structure may vary
            if isinstance(data, list) and len(data) > 0:
                result_data = data[0].get("result", {}).get("data", {})
            else:
                result_data = data.get("result", {}).get("data", {})
            
            if not result_data:
                return None, None
            
            # Convert to DataFrame first
            df = pd.DataFrame(result_data)
            print("Unique metric_ids:")
            print(df['metric_id'].unique())

            
            # Check if we have the required columns
            if 'timestamp' not in df.columns or 'metric_id' not in df.columns or 'value' not in df.columns:
                return df, None  # Return original if structure is different
            
            # Define financial vs operational metrics
            financial_metrics = {
                'trading_volume', 'fees', 'fees_supply_side', 'revenue',
                'market_cap_circulating', 'market_cap_fully_diluted', 'price',
                'token_trading_volume'
            }
            
            operational_metrics = {
                'active_developers', 'code_commits', 'user_dau', 'user_mau', 'user_wau',
                'token_supply_circulating', 'token_turnover_circulating', 'token_turnover_fully_diluted',
                'pf_circulating', 'pf_fully_diluted', 'ps_circulating', 'ps_fully_diluted'
            }
            
            # Convert timestamp to datetime and extract month-year
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['month_year'] = df['timestamp'].dt.strftime('%b %Y')
            
            # Separate financial and operational data
            financial_df = df[df['metric_id'].isin(financial_metrics)]
            operational_df = df[df['metric_id'].isin(operational_metrics)]
            
            def create_formatted_table(data_df, is_financial=True):
                if data_df.empty:
                    return None
                    
                all_metrics = data_df['metric_id'].unique()
                all_months = data_df['month_year'].unique()
                all_months = sorted(all_months, key=lambda x: pd.to_datetime(x, format='%b %Y'), reverse=True)
                
                if len(all_metrics) == 0 or len(all_months) == 0:
                    return None
                
                # Create pivot table
                pivot_df = data_df.pivot_table(
                    index='metric_id', 
                    columns='month_year', 
                    values='value', 
                    aggfunc='mean'
                )
                
                # Calculate percentage changes and format the table with symbols
                formatted_data = {}
                
                for metric in all_metrics:
                    if metric in pivot_df.index:
                        formatted_data[metric.replace('_', ' ').title()] = {}
                        
                        metric_row = pivot_df.loc[metric]
                        
                        for i, month in enumerate(all_months):
                            if month in metric_row.index and not pd.isna(metric_row[month]):
                                value = metric_row[month]
                                
                                # Calculate percentage change from previous month
                                if i < len(all_months) - 1:
                                    prev_month = all_months[i + 1]
                                    if prev_month in metric_row.index and not pd.isna(metric_row[prev_month]):
                                        prev_value = metric_row[prev_month]
                                        if prev_value != 0:
                                            pct_change = ((value - prev_value) / prev_value) * 100
                                            
                                            # Add symbols and format
                                            if pct_change > 0:
                                                symbol = "🟢"
                                                prefix = "$" if is_financial else ""
                                                formatted_value = f"{self.format_number(value, prefix)}  {symbol}(+{pct_change:.1f}%)"
                                            elif pct_change < 0:
                                                symbol = "🔴"
                                                prefix = "$" if is_financial else ""
                                                formatted_value = f"{self.format_number(value, prefix)}  {symbol}({pct_change:.1f}%)"
                                            else:
                                                symbol = "⚪"
                                                prefix = "$" if is_financial else ""
                                                formatted_value = f"{self.format_number(value, prefix)}  {symbol}(0.0%)"
                                        else:
                                            prefix = "$" if is_financial else ""
                                            formatted_value = f"{self.format_number(value, prefix)} (N/A)"
                                    else:
                                        prefix = "$" if is_financial else ""
                                        formatted_value = f"{self.format_number(value, prefix)} (N/A)"
                                else:
                                    prefix = "$" if is_financial else ""
                                    formatted_value = f"{self.format_number(value, prefix)} (N/A)"
                                
                                formatted_data[metric.replace('_', ' ').title()][month] = formatted_value
                            else:
                                # Handle missing data
                                formatted_data[metric.replace('_', ' ').title()][month] = "N/A"
                
                # Convert to DataFrame with proper column order (most recent first)
                result_df = pd.DataFrame(formatted_data).T
                result_df = result_df.reindex(columns=all_months)
                
                return result_df
            
            financial_table = create_formatted_table(financial_df, is_financial=True)
            operational_table = create_formatted_table(operational_df, is_financial=False)
            
            return financial_table, operational_table
            
        except Exception as e:
            print(f"Error processing financial statement: {e}")
            return None, None
    
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
    
    def aggregate_daily_to_weekly(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate daily data to weekly for better chart readability"""
        if df is None or df.empty or 'timestamp' not in df.columns or 'value' not in df.columns:
            return df
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['week'] = df['timestamp'].dt.to_period('W').dt.start_time
        
        # Aggregate by week - use mean for ratios, sum for volumes/counts
        metric_id = df['metric_id'].iloc[0] if 'metric_id' in df.columns else 'unknown'
        
        # Use sum for volume/count metrics, mean for others
        agg_func = 'sum' if any(keyword in metric_id.lower() for keyword in ['volume', 'fees', 'revenue', 'user']) else 'mean'
        
        weekly_df = df.groupby(['week', 'metric_id']).agg({
            'value': agg_func,
            'data_id': 'first'
        }).reset_index()
        
        weekly_df['timestamp'] = weekly_df['week']
        return weekly_df[['data_id', 'metric_id', 'value', 'timestamp']]

    def aggregate_daily_to_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate daily data to monthly for better chart readability"""
        if df is None or df.empty or 'timestamp' not in df.columns or 'value' not in df.columns:
            return df
        
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['month'] = df['timestamp'].dt.to_period('M').dt.start_time
        
        # Aggregate by month
        metric_id = df['metric_id'].iloc[0] if 'metric_id' in df.columns else 'unknown'
        
        # Use sum for volume/count metrics, mean for others
        agg_func = 'sum' if any(keyword in metric_id.lower() for keyword in ['volume', 'fees', 'revenue', 'user']) else 'mean'
        
        monthly_df = df.groupby(['month', 'metric_id']).agg({
            'value': agg_func,
            'data_id': 'first'
        }).reset_index()
        
        monthly_df['timestamp'] = monthly_df['month']
        return monthly_df[['data_id', 'metric_id', 'value', 'timestamp']]
    
    # Charts
    def create_revenue_fees_pie(self, metrics_data: Dict[str, Any]) -> go.Figure:
        """Create pie chart showing revenue vs fees breakdown"""
        fig = go.Figure()
        
        revenue = metrics_data.get('revenue', {}).get('latest', 0)
        fees = metrics_data.get('fees', {}).get('latest', 0)
        
        if revenue > 0 or fees > 0:
            fig.add_trace(go.Pie(
                labels=['Revenue', 'Fees'],
                values=[revenue, fees],
                hole=0.4,
                marker_colors=['#00cc96', '#636efa']
            ))
        
        fig.update_layout(
            title="Revenue vs Fees Breakdown",
            template="plotly_dark",
            height=400,
            showlegend=True
        )
        
        return fig

    def create_user_engagement_pie(self, metrics_data: Dict[str, Any]) -> go.Figure:
        """Create pie chart showing user engagement ratios"""
        fig = go.Figure()
        
        dau = metrics_data.get('user_dau', {}).get('latest', 0)
        wau = metrics_data.get('user_wau', {}).get('latest', 0)
        mau = metrics_data.get('user_mau', {}).get('latest', 0)
        
        # Calculate ratios - WAU excludes DAU, MAU excludes WAU
        dau_only = dau
        wau_only = max(0, wau - dau)
        mau_only = max(0, mau - wau)
        
        if dau_only > 0 or wau_only > 0 or mau_only > 0:
            fig.add_trace(go.Pie(
                labels=['Daily Active', 'Weekly Active', 'Monthly Active'],
                values=[dau_only, wau_only, mau_only],
                hole=0.4,
                marker_colors=['#ff6692', '#19d3f3', '#ffa15a']
            ))
        
        fig.update_layout(
            title="User Engagement Distribution",
            template="plotly_dark",
            height=400,
            showlegend=True
        )
        
        return fig

    def create_revenue_fees_stacked_bar(self, api_client, use_cache=True) -> go.Figure:
        """Create stacked bar chart showing revenue + fees over time (monthly aggregation)"""
        fig = go.Figure()
        
        # Get time series data for both metrics
        revenue_data = api_client.get_time_series('revenue', use_cache=use_cache)
        fees_data = api_client.get_time_series('fees', use_cache=use_cache)
        
        if revenue_data and fees_data:
            revenue_df = self.process_time_series(revenue_data)
            fees_df = self.process_time_series(fees_data)
            
            if revenue_df is not None and fees_df is not None:
                # Aggregate to monthly data for better readability
                revenue_monthly = self.aggregate_daily_to_monthly(revenue_df)
                fees_monthly = self.aggregate_daily_to_monthly(fees_df)
                
                # Merge on timestamp
                merged_df = pd.merge(
                    revenue_monthly[['timestamp', 'value']].rename(columns={'value': 'revenue'}),
                    fees_monthly[['timestamp', 'value']].rename(columns={'value': 'fees'}),
                    on='timestamp',
                    how='outer'
                ).fillna(0)
                
                merged_df = merged_df.sort_values('timestamp')
                
                fig.add_trace(go.Bar(
                    x=merged_df['timestamp'],
                    y=merged_df['revenue'],
                    name='Revenue',
                    marker_color='#00cc96',
                    hovertemplate='<b>Revenue</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
                ))
                
                fig.add_trace(go.Bar(
                    x=merged_df['timestamp'],
                    y=merged_df['fees'],
                    name='Fees',
                    marker_color='#636efa',
                    hovertemplate='<b>Fees</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
                ))
        
        fig.update_layout(
            title="Monthly Revenue + Fees Trend",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            template="plotly_dark",
            height=500,
            barmode='stack',
            hovermode='x unified'
        )
        
        return fig

    def create_user_growth_stacked_bar(self, api_client, use_cache=True) -> go.Figure:
        """Create stacked bar chart showing user growth patterns (weekly aggregation)"""
        fig = go.Figure()
        
        # Get time series data for user metrics
        dau_data = api_client.get_time_series('user_dau', use_cache=use_cache)
        wau_data = api_client.get_time_series('user_wau', use_cache=use_cache)
        mau_data = api_client.get_time_series('user_mau', use_cache=use_cache)
        
        dataframes = []
        
        if dau_data:
            dau_df = self.process_time_series(dau_data)
            if dau_df is not None:
                dau_weekly = self.aggregate_daily_to_weekly(dau_df)
                dataframes.append(dau_weekly[['timestamp', 'value']].rename(columns={'value': 'dau'}))
        
        if wau_data:
            wau_df = self.process_time_series(wau_data)
            if wau_df is not None:
                wau_weekly = self.aggregate_daily_to_weekly(wau_df)
                dataframes.append(wau_weekly[['timestamp', 'value']].rename(columns={'value': 'wau'}))
        
        if mau_data:
            mau_df = self.process_time_series(mau_data)
            if mau_df is not None:
                mau_weekly = self.aggregate_daily_to_weekly(mau_df)
                dataframes.append(mau_weekly[['timestamp', 'value']].rename(columns={'value': 'mau'}))
        
        if dataframes:
            # Merge all dataframes
            merged_df = dataframes[0]
            for df in dataframes[1:]:
                merged_df = pd.merge(merged_df, df, on='timestamp', how='outer')
            
            merged_df = merged_df.fillna(0).sort_values('timestamp')
            
            colors = ['#ff6692', '#19d3f3', '#ffa15a']
            labels = ['Daily Active Users', 'Weekly Active Users', 'Monthly Active Users']
            
            for i, col in enumerate(['dau', 'wau', 'mau']):
                if col in merged_df.columns:
                    fig.add_trace(go.Bar(
                        x=merged_df['timestamp'],
                        y=merged_df[col],
                        name=labels[i],
                        marker_color=colors[i],
                        hovertemplate=f'<b>{labels[i]}</b><br>Week: %{{x}}<br>Users: %{{y:,.0f}}<extra></extra>'
                    ))
        
        fig.update_layout(
            title="Weekly User Growth Patterns",
            xaxis_title="Week",
            yaxis_title="Number of Users",
            template="plotly_dark",
            height=500,
            barmode='group',  # Changed to group for better comparison
            hovermode='x unified'
        )
        
        return fig

    def create_volume_breakdown_stacked_bar(self, api_client, use_cache=True) -> go.Figure:
        """Create stacked bar chart for trading volume breakdown (monthly aggregation)"""
        fig = go.Figure()
        
        # Get time series data for volume metrics
        trading_volume_data = api_client.get_time_series('trading_volume', use_cache=use_cache)
        token_volume_data = api_client.get_time_series('token_trading_volume', use_cache=use_cache)
        
        if trading_volume_data:
            trading_df = self.process_time_series(trading_volume_data)
            
            if trading_df is not None:
                # Aggregate to monthly data
                trading_monthly = self.aggregate_daily_to_monthly(trading_df)
                
                fig.add_trace(go.Bar(
                    x=trading_monthly['timestamp'],
                    y=trading_monthly['value'],
                    name='Trading Volume',
                    marker_color='#ab63fa',
                    hovertemplate='<b>Trading Volume</b><br>Month: %{x}<br>Volume: $%{y:,.0f}<extra></extra>'
                ))
        
        if token_volume_data:
            token_df = self.process_time_series(token_volume_data)
            
            if token_df is not None:
                # Aggregate to monthly data
                token_monthly = self.aggregate_daily_to_monthly(token_df)
                
                fig.add_trace(go.Bar(
                    x=token_monthly['timestamp'],
                    y=token_monthly['value'],
                    name='Token Volume',
                    marker_color='#FFA15A',
                    hovertemplate='<b>Token Volume</b><br>Month: %{x}<br>Volume: $%{y:,.0f}<extra></extra>'
                ))
        
        fig.update_layout(
            title="Monthly Trading Volume Breakdown",
            xaxis_title="Month",
            yaxis_title="Volume ($)",
            template="plotly_dark",
            height=500,
            barmode='stack',
            hovermode='x unified'
        )
        
        return fig