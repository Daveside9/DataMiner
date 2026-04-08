#!/usr/bin/env python3
"""
Monitor Service - Continuous website monitoring and data collection
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
import sqlite3
import os
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(self, db_path="monitor_data.db"):
        self.db_path = db_path
        self.active_monitors = {}
        self.init_database()
    
    def init_database(self):
        """Initialize the monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                selectors TEXT NOT NULL,
                interval_seconds INTEGER NOT NULL,
                duration_seconds INTEGER,
                change_detection TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                total_checks INTEGER DEFAULT 0,
                changes_detected INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scraped_data TEXT,
                has_changes BOOLEAN DEFAULT 0,
                change_type TEXT,
                error_message TEXT,
                FOREIGN KEY (session_id) REFERENCES monitor_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    async def start_monitor(self, config: Dict[str, Any]) -> int:
        """Start a new monitoring session"""
        session_id = self._create_session(config)
        
        monitor_task = asyncio.create_task(
            self._monitor_loop(session_id, config)
        )
        
        self.active_monitors[session_id] = {
            'task': monitor_task,
            'config': config,
            'status': 'active',
            'start_time': datetime.now(),
            'last_check': None,
            'total_checks': 0,
            'changes_detected': 0
        }
        
        logger.info(f"Started monitor session {session_id} for {config['url']}")
        return session_id
    
    def _create_session(self, config: Dict[str, Any]) -> int:
        """Create a new monitoring session in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitor_sessions 
            (url, selectors, interval_seconds, duration_seconds, change_detection)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            config['url'],
            json.dumps(config['selectors']),
            config['interval'],
            config.get('duration', -1),
            config.get('change_detection', 'any')
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    async def _monitor_loop(self, session_id: int, config: Dict[str, Any]):
        """Main monitoring loop for a session"""
        url = config['url']
        selectors = config['selectors']
        interval = config['interval']
        duration = config.get('duration', -1)
        change_detection = config.get('change_detection', 'any')
        
        start_time = time.time()
        last_data = None
        
        try:
            while session_id in self.active_monitors:
                # Check if duration limit reached
                if duration > 0 and (time.time() - start_time) >= duration:
                    logger.info(f"Monitor {session_id} reached duration limit")
                    break
                
                # Check if monitor is paused
                if self.active_monitors[session_id]['status'] == 'paused':
                    await asyncio.sleep(1)
                    continue
                
                # Perform scraping
                try:
                    scraped_data = await self._scrape_website(url, selectors)
                    has_changes = self._detect_changes(scraped_data, last_data, change_detection)
                    change_type = self._get_change_type(scraped_data, last_data) if has_changes else None
                    
                    # Store data
                    self._store_data_point(session_id, scraped_data, has_changes, change_type)
                    
                    # Update monitor stats
                    monitor = self.active_monitors[session_id]
                    monitor['last_check'] = datetime.now()
                    monitor['total_checks'] += 1
                    if has_changes:
                        monitor['changes_detected'] += 1
                    
                    last_data = scraped_data
                    
                    logger.info(f"Monitor {session_id}: Check #{monitor['total_checks']}, Changes: {has_changes}")
                    
                except Exception as e:
                    logger.error(f"Monitor {session_id} scraping error: {e}")
                    self._store_data_point(session_id, None, False, None, str(e))
                
                # Wait for next check
                await asyncio.sleep(interval)
        
        except asyncio.CancelledError:
            logger.info(f"Monitor {session_id} was cancelled")
        except Exception as e:
            logger.error(f"Monitor {session_id} error: {e}")
        finally:
            # Clean up
            if session_id in self.active_monitors:
                del self.active_monitors[session_id]
            self._end_session(session_id)
    
    async def _scrape_website(self, url: str, selectors: Dict[str, str]) -> Dict[str, List[str]]:
        """Scrape website using the main scraping API"""
        api_url = "http://localhost:5000/api/scrape"
        
        payload = {
            "url": url,
            "selectors": selectors,
            "use_selenium": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success'):
                        return result['data']['data']
                    else:
                        raise Exception(result.get('error', 'Scraping failed'))
                else:
                    raise Exception(f"HTTP {response.status}")
    
    def _detect_changes(self, new_data: Dict, old_data: Dict, change_type: str) -> bool:
        """Detect if data has changed based on change detection type"""
        if not old_data:
            return False
        
        if change_type == 'any':
            return json.dumps(new_data, sort_keys=True) != json.dumps(old_data, sort_keys=True)
        elif change_type == 'new_data':
            return any(
                len(new_data.get(key, [])) > len(old_data.get(key, []))
                for key in new_data.keys()
            )
        elif change_type == 'score_change':
            return (json.dumps(new_data.get('scores', []), sort_keys=True) != 
                   json.dumps(old_data.get('scores', []), sort_keys=True))
        elif change_type == 'status_change':
            return (json.dumps(new_data.get('status', []), sort_keys=True) != 
                   json.dumps(old_data.get('status', []), sort_keys=True))
        else:
            return False
    
    def _get_change_type(self, new_data: Dict, old_data: Dict) -> str:
        """Determine what type of change occurred"""
        if not old_data:
            return "Initial data"
        
        changes = []
        for key in new_data.keys():
            if json.dumps(new_data.get(key, []), sort_keys=True) != json.dumps(old_data.get(key, []), sort_keys=True):
                changes.append(key)
        
        return f"Changed: {', '.join(changes)}" if changes else "Unknown change"
    
    def _store_data_point(self, session_id: int, data: Optional[Dict], 
                         has_changes: bool, change_type: Optional[str], 
                         error: Optional[str] = None):
        """Store a data point in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitor_data 
            (session_id, scraped_data, has_changes, change_type, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            json.dumps(data) if data else None,
            has_changes,
            change_type,
            error
        ))
        
        conn.commit()
        conn.close()
    
    def _end_session(self, session_id: int):
        """Mark a monitoring session as ended"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session stats
        monitor = self.active_monitors.get(session_id, {})
        total_checks = monitor.get('total_checks', 0)
        changes_detected = monitor.get('changes_detected', 0)
        
        cursor.execute('''
            UPDATE monitor_sessions 
            SET end_time = CURRENT_TIMESTAMP, status = 'completed',
                total_checks = ?, changes_detected = ?
            WHERE id = ?
        ''', (total_checks, changes_detected, session_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Session {session_id} ended. Checks: {total_checks}, Changes: {changes_detected}")
    
    def pause_monitor(self, session_id: int) -> bool:
        """Pause a monitoring session"""
        if session_id in self.active_monitors:
            self.active_monitors[session_id]['status'] = 'paused'
            logger.info(f"Monitor {session_id} paused")
            return True
        return False
    
    def resume_monitor(self, session_id: int) -> bool:
        """Resume a paused monitoring session"""
        if session_id in self.active_monitors:
            self.active_monitors[session_id]['status'] = 'active'
            logger.info(f"Monitor {session_id} resumed")
            return True
        return False
    
    def stop_monitor(self, session_id: int) -> bool:
        """Stop a monitoring session"""
        if session_id in self.active_monitors:
            monitor = self.active_monitors[session_id]
            monitor['task'].cancel()
            logger.info(f"Monitor {session_id} stopped")
            return True
        return False
    
    def get_monitor_status(self, session_id: int) -> Optional[Dict]:
        """Get the status of a monitoring session"""
        if session_id in self.active_monitors:
            monitor = self.active_monitors[session_id]
            return {
                'session_id': session_id,
                'status': monitor['status'],
                'url': monitor['config']['url'],
                'start_time': monitor['start_time'].isoformat(),
                'last_check': monitor['last_check'].isoformat() if monitor['last_check'] else None,
                'total_checks': monitor['total_checks'],
                'changes_detected': monitor['changes_detected'],
                'uptime_minutes': (datetime.now() - monitor['start_time']).total_seconds() / 60
            }
        return None
    
    def list_active_monitors(self) -> List[Dict]:
        """List all active monitoring sessions"""
        return [
            self.get_monitor_status(session_id) 
            for session_id in self.active_monitors.keys()
        ]
    
    def get_monitor_data(self, session_id: int, limit: int = 100) -> List[Dict]:
        """Get monitoring data for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, scraped_data, has_changes, change_type, error_message
            FROM monitor_data 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'data': json.loads(row[1]) if row[1] else None,
                'has_changes': bool(row[2]),
                'change_type': row[3],
                'error': row[4]
            }
            for row in rows
        ]
    
    def export_monitor_data(self, session_id: int, format: str = 'json') -> str:
        """Export monitoring data in various formats"""
        data = self.get_monitor_data(session_id, limit=10000)
        
        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Timestamp', 'Has Changes', 'Change Type', 'Error', 'Data'])
            
            # Write data
            for item in data:
                writer.writerow([
                    item['timestamp'],
                    item['has_changes'],
                    item['change_type'] or '',
                    item['error'] or '',
                    json.dumps(item['data']) if item['data'] else ''
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

# Global monitor service instance
monitor_service = MonitorService()

async def main():
    """Demo the monitor service"""
    print("🔧 Monitor Service Demo")
    print("=" * 40)
    
    # Example configuration
    config = {
        'url': 'https://quotes.toscrape.com',
        'selectors': {
            'quotes': '.quote .text',
            'authors': '.quote .author',
            'tags': '.quote .tags a'
        },
        'interval': 30,  # 30 seconds
        'duration': 300,  # 5 minutes
        'change_detection': 'any'
    }
    
    print(f"Starting monitor for: {config['url']}")
    session_id = await monitor_service.start_monitor(config)
    
    # Monitor for a while
    for i in range(10):
        await asyncio.sleep(10)
        status = monitor_service.get_monitor_status(session_id)
        if status:
            print(f"Status: {status['total_checks']} checks, {status['changes_detected']} changes")
        else:
            break
    
    # Stop monitor
    monitor_service.stop_monitor(session_id)
    print("Monitor stopped")

if __name__ == "__main__":
    asyncio.run(main())