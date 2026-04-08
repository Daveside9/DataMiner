#!/usr/bin/env python3
"""
BetVision Pro - Authentication Backend
User registration, login, and session management
"""

import sqlite3
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os

class AuthBackend:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        CORS(self.app, supports_credentials=True)
        
        # JWT settings
        self.jwt_secret = secrets.token_hex(32)
        self.jwt_algorithm = 'HS256'
        
        self.init_database()
        self.setup_routes()
    
    def init_database(self):
        """Initialize user database"""
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                subscription_plan TEXT DEFAULT 'free',
                monitoring_sessions INTEGER DEFAULT 0,
                total_screenshots INTEGER DEFAULT 0
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create monitoring history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                site_url TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                screenshots_count INTEGER DEFAULT 0,
                changes_detected INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def setup_routes(self):
        """Setup authentication routes"""
        
        @self.app.route('/api/auth/register', methods=['POST'])
        def register():
            data = request.get_json()
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            full_name = data.get('full_name', '').strip()
            
            # Validation
            if not all([username, email, password, full_name]):
                return jsonify({'error': 'All fields are required'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            if '@' not in email:
                return jsonify({'error': 'Invalid email format'}), 400
            
            try:
                conn = sqlite3.connect('data/users.db')
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
                if cursor.fetchone():
                    return jsonify({'error': 'Username or email already exists'}), 400
                
                # Hash password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Insert user
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash, full_name))
                
                user_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Generate JWT token
                token = self.generate_jwt_token(user_id, username)
                
                return jsonify({
                    'success': True,
                    'message': 'Registration successful',
                    'user': {
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'subscription_plan': 'free'
                    },
                    'token': token
                })
                
            except Exception as e:
                return jsonify({'error': f'Registration failed: {str(e)}'}), 500
        
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
            
            try:
                conn = sqlite3.connect('data/users.db')
                cursor = conn.cursor()
                
                # Find user by username or email
                cursor.execute('''
                    SELECT id, username, email, password_hash, full_name, subscription_plan, 
                           monitoring_sessions, total_screenshots
                    FROM users 
                    WHERE (username = ? OR email = ?) AND is_active = 1
                ''', (username, username))
                
                user = cursor.fetchone()
                if not user:
                    return jsonify({'error': 'Invalid credentials'}), 401
                
                # Verify password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if password_hash != user[3]:
                    return jsonify({'error': 'Invalid credentials'}), 401
                
                # Update last login
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
                conn.commit()
                conn.close()
                
                # Generate JWT token
                token = self.generate_jwt_token(user[0], user[1])
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'full_name': user[4],
                        'subscription_plan': user[5],
                        'monitoring_sessions': user[6],
                        'total_screenshots': user[7]
                    },
                    'token': token
                })
                
            except Exception as e:
                return jsonify({'error': f'Login failed: {str(e)}'}), 500
        
        @self.app.route('/api/auth/profile', methods=['GET'])
        def get_profile():
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                user_id = payload['user_id']
                
                conn = sqlite3.connect('data/users.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, full_name, subscription_plan, 
                           monitoring_sessions, total_screenshots, created_at, last_login
                    FROM users WHERE id = ? AND is_active = 1
                ''', (user_id,))
                
                user = cursor.fetchone()
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                conn.close()
                
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'full_name': user[3],
                        'subscription_plan': user[4],
                        'monitoring_sessions': user[5],
                        'total_screenshots': user[6],
                        'created_at': user[7],
                        'last_login': user[8]
                    }
                })
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                return jsonify({'error': f'Profile fetch failed: {str(e)}'}), 500
        
        @self.app.route('/api/auth/logout', methods=['POST'])
        def logout():
            return jsonify({'success': True, 'message': 'Logged out successfully'})
        
        @self.app.route('/api/auth/stats', methods=['GET'])
        def get_user_stats():
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                user_id = payload['user_id']
                
                conn = sqlite3.connect('data/users.db')
                cursor = conn.cursor()
                
                # Get monitoring history
                cursor.execute('''
                    SELECT COUNT(*) as total_sessions,
                           SUM(screenshots_count) as total_screenshots,
                           SUM(changes_detected) as total_changes
                    FROM monitoring_history WHERE user_id = ?
                ''', (user_id,))
                
                stats = cursor.fetchone()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'stats': {
                        'total_sessions': stats[0] or 0,
                        'total_screenshots': stats[1] or 0,
                        'total_changes': stats[2] or 0
                    }
                })
                
            except Exception as e:
                return jsonify({'error': f'Stats fetch failed: {str(e)}'}), 500
    
    def generate_jwt_token(self, user_id, username):
        """Generate JWT token for user"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except:
            return None
    
    def run_server(self, host='localhost', port=5004):
        """Run the authentication server"""
        print(f"🔐 BetVision Pro - Authentication Server starting...")
        print(f"📡 API Server: http://{host}:{port}")
        print(f"🌐 Features: User registration, login, JWT tokens, session management")
        print("=" * 70)
        
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main function"""
    auth = AuthBackend()
    
    print("🔐 BetVision Pro - Authentication System")
    print("=" * 70)
    print("✅ Features:")
    print("   👤 User registration and login")
    print("   🔒 Secure password hashing")
    print("   🎫 JWT token authentication")
    print("   📊 User statistics tracking")
    print("   💾 SQLite database storage")
    print("=" * 70)
    
    try:
        auth.run_server()
    except KeyboardInterrupt:
        print("\n🛑 Authentication server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()