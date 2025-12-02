# auth.py
# -*- coding: utf-8 -*-
"""
Authentication system using SQLite for Bot Manager
Extended with Bot Ownership Management
"""
import sqlite3
import hashlib
import secrets
import datetime
from pathlib import Path
import string
import random
import json

class AuthDB:
    def __init__(self, db_path='data/users.db'):
        self.db_path = db_path
        Path('data').mkdir(exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                fullname TEXT,
                phone TEXT,
                birthday TEXT,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Password reset tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Bots table - Lưu thông tin bot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'offline',
                bot_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Bot access tokens - Để xác thực bot khi kết nối
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return self.hash_password(password) == password_hash
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, username, email, password, fullname=None):
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, fullname)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, fullname))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {'success': True, 'user_id': user_id}
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def authenticate(self, username_or_email, password):
        """Authenticate user and create session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Try to find user by username or email
        cursor.execute('''
            SELECT * FROM users 
            WHERE (username = ? OR email = ?) AND is_active = 1
        ''', (username_or_email, username_or_email))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {'success': False, 'error': 'Invalid credentials'}
        
        if not self.verify_password(password, user['password_hash']):
            conn.close()
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(days=7)
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        ''', (user['id'], session_token, expires_at))
        
        # Update last login
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user['id'],))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'session_token': session_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'fullname': user['fullname'],
                'role': user['role']
            }
        }
    
    def validate_session(self, session_token):
        """Validate session token and return user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, s.expires_at
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            AND u.is_active = 1
        ''', (session_token,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return None
        
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'fullname': user['fullname'],
            'phone': user['phone'],
            'birthday': user['birthday'],
            'gender': user['gender'],
            'role': user['role']
        }
    
    def logout(self, session_token):
        """Invalidate session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return None
        
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'fullname': user['fullname'],
            'phone': user['phone'],
            'birthday': user['birthday'],
            'gender': user['gender'],
            'role': user['role'],
            'created_at': user['created_at'],
            'last_login': user['last_login']
        }
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['fullname', 'phone', 'birthday', 'gender', 'email']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f'{field} = ?')
                values.append(kwargs[field])
        
        if not updates:
            conn.close()
            return {'success': False, 'error': 'No fields to update'}
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return {'success': True}
        except sqlite3.IntegrityError as e:
            conn.close()
            return {'success': False, 'error': str(e)}
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {'success': False, 'error': 'User not found'}
        
        if not self.verify_password(old_password, user['password_hash']):
            conn.close()
            return {'success': False, 'error': 'Incorrect password'}
        
        new_hash = self.hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user_id))
        
        # Invalidate all sessions
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def create_password_reset_token(self, email):
        """Create password reset token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {'success': False, 'error': 'Email not found'}
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        cursor.execute('''
            INSERT INTO password_resets (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user['id'], token, expires_at))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'token': token}
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM password_resets
            WHERE token = ? AND expires_at > CURRENT_TIMESTAMP AND used = 0
        ''', (token,))
        
        reset = cursor.fetchone()
        
        if not reset:
            conn.close()
            return {'success': False, 'error': 'Invalid or expired token'}
        
        new_hash = self.hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                      (new_hash, reset['user_id']))
        
        cursor.execute('UPDATE password_resets SET used = 1 WHERE token = ?', (token,))
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (reset['user_id'],))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def delete_user(self, user_id):
        """Delete user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM password_resets WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    # ==================== BOT MANAGEMENT METHODS ====================
    
    def generate_bot_id(self):
        """Generate unique 6-character bot ID (uppercase and lowercase)"""
        chars = string.ascii_letters  # a-z, A-Z
        max_attempts = 100
        
        for _ in range(max_attempts):
            bot_id = ''.join(random.choice(chars) for _ in range(6))
            
            # Check if ID already exists
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM bots WHERE id = ?', (bot_id,))
            exists = cursor.fetchone()
            conn.close()
            
            if not exists:
                return bot_id
        
        raise Exception('Failed to generate unique bot ID after maximum attempts')
    
    def create_bot(self, user_id, name, metadata=None):
        """Create a new bot for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        bot_id = self.generate_bot_id()
        token = secrets.token_urlsafe(32)
        
        try:
            # Insert bot
            cursor.execute('''
                INSERT INTO bots (id, user_id, name, metadata)
                VALUES (?, ?, ?, ?)
            ''', (bot_id, user_id, name, str(metadata or {})))
            
            # Create bot token
            cursor.execute('''
                INSERT INTO bot_tokens (bot_id, token)
                VALUES (?, ?)
            ''', (bot_id, token))
            
            conn.commit()
            
            return {
                'success': True,
                'bot_id': bot_id,
                'token': token
            }
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_user_bots(self, user_id):
        """Get all bots owned by user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.*, bt.token
            FROM bots b
            LEFT JOIN bot_tokens bt ON b.id = bt.bot_id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        ''', (user_id,))
        
        bots = cursor.fetchall()
        conn.close()
        
        return [{
            'id': bot['id'],
            'name': bot['name'],
            'status': bot['status'],
            'created_at': bot['created_at'],
            'last_active': bot['last_active'],
            'metadata': bot['metadata'],
            'token': bot['token']
        } for bot in bots]
    
    def get_bot(self, bot_id):
        """Get bot by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM bots WHERE id = ?', (bot_id,))
        bot = cursor.fetchone()
        conn.close()
        
        if not bot:
            return None
        
        return {
            'id': bot['id'],
            'user_id': bot['user_id'],
            'name': bot['name'],
            'status': bot['status'],
            'bot_data': bot['bot_data'],
            'created_at': bot['created_at'],
            'last_active': bot['last_active'],
            'metadata': bot['metadata']
        }
    
    def verify_bot_token(self, bot_id, token):
        """Verify bot token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bt.*, b.user_id, b.name
            FROM bot_tokens bt
            JOIN bots b ON bt.bot_id = b.id
            WHERE bt.bot_id = ? AND bt.token = ?
        ''', (bot_id, token))
        
        result = cursor.fetchone()
        
        if result:
            # Update last used
            cursor.execute('''
                UPDATE bot_tokens SET last_used = CURRENT_TIMESTAMP
                WHERE bot_id = ? AND token = ?
            ''', (bot_id, token))
            conn.commit()
        
        conn.close()
        
        return result is not None
    
    def verify_bot_ownership(self, user_id, bot_id):
        """Verify if user owns the bot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM bots WHERE id = ? AND user_id = ?
        ''', (bot_id, user_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def update_bot_status(self, bot_id, status, bot_data=None):
        """Update bot status and data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if bot_data:
            cursor.execute('''
                UPDATE bots 
                SET status = ?, bot_data = ?, last_active = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, bot_data, bot_id))
        else:
            cursor.execute('''
                UPDATE bots 
                SET status = ?, last_active = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, bot_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def update_bot_data(self, bot_id, bot_data):
        """Update bot data (groups, friends, etc.)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bots 
            SET bot_data = ?, last_active = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (json.dumps(bot_data), bot_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def get_bot_data(self, bot_id):
        """Get bot data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT bot_data FROM bots WHERE id = ?', (bot_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result['bot_data']:
            return None
        
        try:
            return json.loads(result['bot_data'])
        except:
            return None
    
    def delete_bot(self, bot_id, user_id):
        """Delete bot (must be owner)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM bots WHERE id = ? AND user_id = ?
        ''', (bot_id, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            return {'success': True}
        return {'success': False, 'error': 'Bot not found or not authorized'}
    
    def update_bot_info(self, bot_id, user_id, **kwargs):
        """Update bot info (name, metadata)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verify ownership first
        if not self.verify_bot_ownership(user_id, bot_id):
            conn.close()
            return {'success': False, 'error': 'Not authorized'}
        
        allowed_fields = ['name', 'metadata']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f'{field} = ?')
                values.append(str(kwargs[field]) if field == 'metadata' else kwargs[field])
        
        if not updates:
            conn.close()
            return {'success': False, 'error': 'No fields to update'}
        
        values.append(bot_id)
        query = f"UPDATE bots SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def get_all_bots(self):
        """Get all bots in the system (admin function)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.*, u.username, u.email
            FROM bots b
            JOIN users u ON b.user_id = u.id
            ORDER BY b.created_at DESC
        ''')
        
        bots = cursor.fetchall()
        conn.close()
        
        return [{
            'id': bot['id'],
            'name': bot['name'],
            'status': bot['status'],
            'user_id': bot['user_id'],
            'username': bot['username'],
            'email': bot['email'],
            'created_at': bot['created_at'],
            'last_active': bot['last_active'],
            'metadata': bot['metadata']
        } for bot in bots]
    
    def get_bot_token(self, bot_id, user_id):
        """Get bot token (only owner can access)"""
        if not self.verify_bot_ownership(user_id, bot_id):
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT token FROM bot_tokens WHERE bot_id = ?
        ''', (bot_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['token'] if result else None
    
    def regenerate_bot_token(self, bot_id, user_id):
        """Regenerate bot token (only owner)"""
        if not self.verify_bot_ownership(user_id, bot_id):
            return {'success': False, 'error': 'Not authorized'}
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        new_token = secrets.token_urlsafe(32)
        
        try:
            # Delete old token
            cursor.execute('DELETE FROM bot_tokens WHERE bot_id = ?', (bot_id,))
            
            # Create new token
            cursor.execute('''
                INSERT INTO bot_tokens (bot_id, token)
                VALUES (?, ?)
            ''', (bot_id, new_token))
            
            conn.commit()
            
            return {'success': True, 'token': new_token}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()


# Convenience functions
def create_auth_db(db_path='data/users.db'):
    """Create and return AuthDB instance"""
    return AuthDB(db_path)


if __name__ == '__main__':
    # Test the database initialization
    print("Initializing database...")
    auth_db = AuthDB()
    print("✅ Database initialized successfully!")
    print(f"📁 Database location: {auth_db.db_path}")