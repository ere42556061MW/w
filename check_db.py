# check_db.py
# -*- coding: utf-8 -*-
"""
Script để kiểm tra và quản lý database
"""
from auth import AuthDB
import sys

def main():
    auth_db = AuthDB()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_db.py list - Liệt kê users")
        print("  python check_db.py create <username> <email> <password> - Tạo user")
        print("  python check_db.py delete <user_id> - Xóa user")
        print("  python check_db.py sessions - Liệt kê sessions")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        
        print(f"\nTotal users: {len(users)}\n")
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Fullname: {user['fullname']}")
            print(f"Role: {user['role']}")
            print(f"Created: {user['created_at']}")
            print(f"Last login: {user['last_login']}")
            print("-" * 50)
    
    elif command == 'create':
        if len(sys.argv) < 5:
            print("Usage: python check_db.py create <username> <email> <password>")
            return
        
        username = sys.argv[2]
        email = sys.argv[3]
        password = sys.argv[4]
        
        result = auth_db.create_user(username, email, password)
        
        if result['success']:
            print(f"✅ User created successfully! ID: {result['user_id']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Usage: python check_db.py delete <user_id>")
            return
        
        user_id = int(sys.argv[2])
        auth_db.delete_user(user_id)
        print(f"✅ User {user_id} deleted")
    
    elif command == 'sessions':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, u.username 
            FROM sessions s 
            JOIN users u ON s.user_id = u.id
        ''')
        sessions = cursor.fetchall()
        conn.close()
        
        print(f"\nActive sessions: {len(sessions)}\n")
        for session in sessions:
            print(f"User: {session['username']}")
            print(f"Token: {session['session_token'][:20]}...")
            print(f"Expires: {session['expires_at']}")
            print("-" * 50)

if __name__ == '__main__':
    main()