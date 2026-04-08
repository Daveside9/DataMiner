import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path="data/dataminer.db"):
        self.db_path = db_path
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create scraped_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT NOT NULL,
                source_name TEXT,
                data_json TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                scrape_method TEXT,
                success BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create data_sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                selectors_json TEXT,
                description TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_scraped DATETIME
            )
        ''')
        
        # Create analysis_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                results_json TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def store_scraped_data(self, url: str, scraped_data: Dict[str, Any], source_name: str = None):
        """Store scraped data in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract source name from URL if not provided
        if not source_name:
            source_name = url.split('/')[2]  # Get domain name
        
        cursor.execute('''
            INSERT INTO scraped_data (source_url, source_name, data_json, scrape_method, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            url,
            source_name,
            json.dumps(scraped_data),
            scraped_data.get('method', 'unknown'),
            'error' not in scraped_data
        ))
        
        # Update last_scraped timestamp for the source
        cursor.execute('''
            UPDATE data_sources 
            SET last_scraped = CURRENT_TIMESTAMP 
            WHERE name = ?
        ''', (source_name,))
        
        conn.commit()
        conn.close()
    
    def get_historical_data(self, source_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data for a specific source"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, source_url, data_json, timestamp, scrape_method, success
            FROM scraped_data 
            WHERE source_name = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (source_name, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            try:
                parsed_data = json.loads(row[2])
                data.append({
                    'id': row[0],
                    'source_url': row[1],
                    'data': parsed_data,
                    'timestamp': row[3],
                    'method': row[4],
                    'success': bool(row[5])
                })
            except json.JSONDecodeError:
                continue
        
        return data
    
    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Get all data sources"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ds.name, ds.url, ds.description, ds.active, ds.created_at, ds.last_scraped,
                   COUNT(sd.id) as total_scrapes,
                   MAX(sd.timestamp) as latest_scrape
            FROM data_sources ds
            LEFT JOIN scraped_data sd ON ds.name = sd.source_name
            GROUP BY ds.name, ds.url, ds.description, ds.active, ds.created_at, ds.last_scraped
            ORDER BY ds.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        sources = []
        for row in rows:
            sources.append({
                'name': row[0],
                'url': row[1],
                'description': row[2],
                'active': bool(row[3]),
                'created_at': row[4],
                'last_scraped': row[5],
                'total_scrapes': row[6],
                'latest_scrape': row[7]
            })
        
        return sources
    
    def add_data_source(self, name: str, url: str, selectors: Dict[str, str] = None, description: str = None):
        """Add a new data source"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO data_sources (name, url, selectors_json, description)
                VALUES (?, ?, ?, ?)
            ''', (
                name,
                url,
                json.dumps(selectors) if selectors else None,
                description
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Source already exists
        finally:
            conn.close()
    
    def get_data_source(self, name: str) -> Dict[str, Any]:
        """Get a specific data source configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, url, selectors_json, description, active
            FROM data_sources 
            WHERE name = ?
        ''', (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            selectors = json.loads(row[2]) if row[2] else {}
            return {
                'name': row[0],
                'url': row[1],
                'selectors': selectors,
                'description': row[3],
                'active': bool(row[4])
            }
        return None
    
    def store_analysis_results(self, source_name: str, analysis_type: str, results: Dict[str, Any]):
        """Store analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results (source_name, analysis_type, results_json)
            VALUES (?, ?, ?)
        ''', (source_name, analysis_type, json.dumps(results)))
        
        conn.commit()
        conn.close()
    
    def get_latest_analysis(self, source_name: str, analysis_type: str = None) -> Dict[str, Any]:
        """Get the latest analysis results for a source"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if analysis_type:
            cursor.execute('''
                SELECT analysis_type, results_json, timestamp
                FROM analysis_results 
                WHERE source_name = ? AND analysis_type = ?
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (source_name, analysis_type))
        else:
            cursor.execute('''
                SELECT analysis_type, results_json, timestamp
                FROM analysis_results 
                WHERE source_name = ?
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (source_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'analysis_type': row[0],
                'results': json.loads(row[1]),
                'timestamp': row[2]
            }
        return None