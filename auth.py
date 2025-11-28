# auth.py
# -*- coding: utf-8 -*-
"""
Authentication system using SQLite for Bot Manager
"""
import sqlite3
import hashlib
import secrets
import datetime
from pathlib import Path

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
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return self.hash_password(password) == password_hash
    
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