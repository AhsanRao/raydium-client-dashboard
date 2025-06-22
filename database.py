import sqlite3
import json
import datetime
from typing import Optional, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Financial statement cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_statements (
                id INTEGER PRIMARY KEY,
                project_slug TEXT,
                granularity TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_slug, granularity)
            )
        ''')
        
        # Metrics breakdown cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_breakdown (
                id INTEGER PRIMARY KEY,
                project_slug TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_slug)
            )
        ''')
        
        # Time series cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_series (
                id INTEGER PRIMARY KEY,
                project_slug TEXT,
                metric_id TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_slug, metric_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_data_fresh(self, table: str, identifier: Dict[str, str], hours: int = 1) -> bool:
        """Check if cached data is fresh"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where_clause = " AND ".join([f"{k} = ?" for k in identifier.keys()])
        query = f'''
            SELECT created_at FROM {table} 
            WHERE {where_clause}
        '''
        
        cursor.execute(query, list(identifier.values()))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        created_at = datetime.datetime.fromisoformat(result[0])
        now = datetime.datetime.now()
        return (now - created_at).total_seconds() < hours * 3600
    
    def get_cached_data(self, table: str, identifier: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Get cached data if fresh"""
        if not self.is_data_fresh(table, identifier):
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        where_clause = " AND ".join([f"{k} = ?" for k in identifier.keys()])
        query = f'''
            SELECT data FROM {table} 
            WHERE {where_clause}
        '''
        
        cursor.execute(query, list(identifier.values()))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def cache_data(self, table: str, identifier: Dict[str, str], data: Dict[str, Any]):
        """Cache data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create the INSERT OR REPLACE query
        columns = list(identifier.keys()) + ['data']
        placeholders = ', '.join(['?' for _ in columns])
        values = list(identifier.values()) + [json.dumps(data)]
        
        query = f'''
            INSERT OR REPLACE INTO {table} 
            ({', '.join(columns)}, created_at) 
            VALUES ({placeholders}, CURRENT_TIMESTAMP)
        '''
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()