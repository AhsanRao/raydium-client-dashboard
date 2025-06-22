import requests
import json
import random
import time
from fake_useragent import UserAgent
from typing import Dict, Any, List, Optional

from config import BREAKDOWN_API, DB_PATH, FINANCIAL_STATEMENT_API, TIMESERIES_API
from database import DatabaseManager

class TokenTerminalAPI:
    def __init__(self, bearer_token: str, jwt_token: str):
        self.bearer_token = bearer_token
        self.jwt_token = jwt_token
        self.ua = UserAgent()
        self.db = DatabaseManager(DB_PATH)
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers with random user agent"""
        return {
            'accept': '*/*',
            'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
            'authorization': f'Bearer {self.bearer_token}',
            'content-type': 'application/json',
            'origin': 'https://tokenterminal.com',
            'referer': 'https://tokenterminal.com/explorer/projects/raydium/financial-statement',
            'user-agent': self.ua.random,
            'x-tt-terminal-jwt': self.jwt_token,
        }
    
    def _make_request(self, url: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with retry logic"""
        headers = self._get_headers()
        
        for attempt in range(3):
            try:
                if data:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
                else:
                    response = requests.get(url, params=params, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    time.sleep(2 ** attempt)
                    continue
                else:
                    print(f"API Error: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(1)
                continue
        
        return None
    
    def get_financial_statement(self, project_slug: str = "raydium", granularity: str = "month", use_cache: bool = True) -> Optional[Dict]:
        """Get financial statement data"""
        cache_key = {"project_slug": project_slug, "granularity": granularity}
        
        if use_cache:
            cached = self.db.get_cached_data("financial_statements", cache_key)
            if cached:
                return cached
        
        input_data = {
            "0": {
                "project_slug": project_slug,
                "granularity": granularity
            }
        }
        
        params = {
            "batch": "1",
            "input": json.dumps(input_data)
        }
        
        data = self._make_request(FINANCIAL_STATEMENT_API, params=params)
        
        if data and use_cache:
            self.db.cache_data("financial_statements", cache_key, data)
        
        return data
    
    def get_metrics_breakdown(self, project_slug: str = "raydium", use_cache: bool = True) -> Optional[Dict]:
        """Get metrics breakdown data"""
        cache_key = {"project_slug": project_slug}
        
        if use_cache:
            cached = self.db.get_cached_data("metrics_breakdown", cache_key)
            if cached:
                return cached
        
        payload = {
            "data_ids": [project_slug],
            "metric_ids": [
                "trading_volume", "market_cap_fully_diluted", "token_trading_volume",
                "fees", "revenue", "user_mau", "market_cap_circulating", "tvl",
                "pf_fully_diluted", "pf_circulating", "ps_fully_diluted", "ps_circulating",
                "user_dau", "user_wau", "active_developers", "code_commits", "afpu", "arpu",
                "active_addresses_daily", "active_addresses_monthly", "active_addresses_weekly",
                "fees_supply_side", "gas_used", "liquidity_turnover", "price",
                "token_supply_circulating", "token_turnover_circulating",
                "token_turnover_fully_diluted", "trading_volume_avg_per_user",
                "transaction_count_contracts"
            ],
            "interval": "365d",
            "groupBy": "chain-project",
            "ignore_threshold": False
        }
        
        data = self._make_request(BREAKDOWN_API, data=payload)
        
        if data and use_cache:
            self.db.cache_data("metrics_breakdown", cache_key, data)
        
        return data
    
    def get_time_series(self, metric_id: str, project_slug: str = "raydium", interval: str = "365d", use_cache: bool = True) -> Optional[Dict]:
        """Get time series data for a specific metric"""
        cache_key = {"project_slug": project_slug, "metric_id": metric_id}
        
        if use_cache:
            cached = self.db.get_cached_data("time_series", cache_key)
            if cached:
                return cached
        
        payload = {
            "data_ids": [project_slug],
            "metric_ids": [metric_id],
            "interval": interval,
            "groupBy": "projects"
        }
        
        data = self._make_request(TIMESERIES_API, data=payload)
        
        if data and use_cache:
            self.db.cache_data("time_series", cache_key, data)
        
        return data