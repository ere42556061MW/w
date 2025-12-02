# check_db.py
# -*- coding: utf-8 -*-
"""
Script để kiểm tra và quản lý database
Updated with Bot Management Support
"""
from auth import AuthDB
import sys

def print_help():
    """Print help message"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           📊 DATABASE MANAGEMENT COMMANDS                    ║
╚══════════════════════════════════════════════════════════════╝

👥 USER MANAGEMENT:
  python check_db.py list
    → Liệt kê tất cả users
    
  python check_db.py create <username> <email> <password>
    → Tạo user mới
    
  python check_db.py user <user_id>
    → Xem chi tiết user
    
  python check_db.py delete <user_id>
    → Xóa user (và tất cả bots của user)
    
  python check_db.py sessions
    → Liệt kê active sessions

🤖 BOT MANAGEMENT:
  python check_db.py bots
    → Liệt kê tất cả bots
    
  python check_db.py user-bots <user_id>
    → Liệt kê bots của user cụ thể
    
  python check_db.py bot <bot_id>
    → Xem chi tiết bot

📊 STATISTICS:
  python check_db.py stats
    → Thống kê tổng quan hệ thống

🗑️  CLEANUP:
  python check_db.py cleanup-sessions
    → Xóa các session hết hạn
    
  python check_db.py cleanup-resets
    → Xóa các password reset token đã dùng

═══════════════════════════════════════════════════════════════
""")

def main():
    auth_db = AuthDB()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    # ==================== USER COMMANDS ====================
    
    if command == 'list':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        
        print(f"\n{'='*70}")
        print(f"👥 Total users: {len(users)}")
        print(f"{'='*70}\n")
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Fullname: {user['fullname']}")
            print(f"Role: {user['role']}")
            print(f"Active: {'✅' if user['is_active'] else '❌'}")
            print(f"Created: {user['created_at']}")
            print(f"Last login: {user['last_login'] or 'Never'}")
            
            # Count user's bots
            bots = auth_db.get_user_bots(user['id'])
            print(f"Bots: {len(bots)}")
            print("-" * 70)
    
    elif command == 'create':
        if len(sys.argv) < 5:
            print("❌ Usage: python check_db.py create <username> <email> <password>")
            return
        
        username = sys.argv[2]
        email = sys.argv[3]
        password = sys.argv[4]
        
        result = auth_db.create_user(username, email, password)
        
        if result['success']:
            print(f"\n✅ User created successfully!")
            print(f"User ID: {result['user_id']}")
            print(f"Username: {username}")
            print(f"Email: {email}\n")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command == 'user':
        if len(sys.argv) < 3:
            print("❌ Usage: python check_db.py user <user_id>")
            return
        
        user_id = int(sys.argv[2])
        user = auth_db.get_user_by_id(user_id)
        
        if not user:
            print(f"❌ User ID {user_id} not found")
            return
        
        bots = auth_db.get_user_bots(user_id)
        
        print(f"\n{'='*70}")
        print(f"👤 User Details")
        print(f"{'='*70}\n")
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Fullname: {user['fullname']}")
        print(f"Phone: {user['phone']}")
        print(f"Birthday: {user['birthday']}")
        print(f"Gender: {user['gender']}")
        print(f"Role: {user['role']}")
        print(f"Created: {user['created_at']}")
        print(f"Last Login: {user['last_login'] or 'Never'}")
        print(f"\n🤖 Bots: {len(bots)}")
        
        if bots:
            for bot in bots:
                print(f"  • {bot['id']} - {bot['name']} ({bot['status']})")
        
        print(f"\n{'='*70}\n")
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python check_db.py delete <user_id>")
            return
        
        user_id = int(sys.argv[2])
        user = auth_db.get_user_by_id(user_id)
        
        if not user:
            print(f"❌ User ID {user_id} not found")
            return
        
        bots = auth_db.get_user_bots(user_id)
        
        print(f"\n⚠️  WARNING: You are about to delete user '{user['username']}' (ID: {user_id})")
        if bots:
            print(f"⚠️  This will also delete {len(bots)} bot(s):")
            for bot in bots:
                print(f"    • {bot['id']} - {bot['name']}")
        print(f"\nThis action CANNOT be undone!")
        
        confirm = input(f"\nType 'DELETE' to confirm: ")
        
        if confirm != 'DELETE':
            print("❌ Deletion cancelled.")
            return
        
        auth_db.delete_user(user_id)
        print(f"✅ User {user_id} deleted")
    
    elif command == 'sessions':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, u.username, u.email
            FROM sessions s 
            JOIN users u ON s.user_id = u.id
            WHERE s.expires_at > CURRENT_TIMESTAMP
            ORDER BY s.created_at DESC
        ''')
        sessions = cursor.fetchall()
        conn.close()
        
        print(f"\n{'='*70}")
        print(f"🔑 Active sessions: {len(sessions)}")
        print(f"{'='*70}\n")
        
        for session in sessions:
            print(f"User: {session['username']} ({session['email']})")
            print(f"Token: {session['session_token'][:20]}...{session['session_token'][-10:]}")
            print(f"Created: {session['created_at']}")
            print(f"Expires: {session['expires_at']}")
            print("-" * 70)
    
    # ==================== BOT COMMANDS ====================
    
    elif command == 'bots':
        bots = auth_db.get_all_bots()
        
        print(f"\n{'='*70}")
        print(f"🤖 Total bots: {len(bots)}")
        print(f"{'='*70}\n")
        
        for bot in bots:
            print(f"ID: {bot['id']}")
            print(f"Name: {bot['name']}")
            print(f"Owner: {bot['username']} ({bot['email']})")
            print(f"Status: {bot['status']}")
            print(f"Created: {bot['created_at']}")
            print(f"Last Active: {bot['last_active'] or 'Never'}")
            print("-" * 70)
    
    elif command == 'user-bots':
        if len(sys.argv) < 3:
            print("❌ Usage: python check_db.py user-bots <user_id>")
            return
        
        user_id = int(sys.argv[2])
        user = auth_db.get_user_by_id(user_id)
        
        if not user:
            print(f"❌ User ID {user_id} not found")
            return
        
        bots = auth_db.get_user_bots(user_id)
        
        print(f"\n{'='*70}")
        print(f"🤖 Bots của {user['username']} (ID: {user_id}): {len(bots)}")
        print(f"{'='*70}\n")
        
        if not bots:
            print("📭 No bots found.")
            return
        
        for bot in bots:
            print(f"ID: {bot['id']}")
            print(f"Name: {bot['name']}")
            print(f"Status: {bot['status']}")
            print(f"Created: {bot['created_at']}")
            print(f"Last Active: {bot['last_active'] or 'Never'}")
            print("-" * 70)
    
    elif command == 'bot':
        if len(sys.argv) < 3:
            print("❌ Usage: python check_db.py bot <bot_id>")
            return
        
        bot_id = sys.argv[2]
        bot = auth_db.get_bot(bot_id)
        
        if not bot:
            print(f"❌ Bot {bot_id} not found")
            return
        
        user = auth_db.get_user_by_id(bot['user_id'])
        data = auth_db.get_bot_data(bot_id)
        
        print(f"\n{'='*70}")
        print(f"🤖 Bot Details")
        print(f"{'='*70}\n")
        print(f"ID: {bot['id']}")
        print(f"Name: {bot['name']}")
        print(f"Status: {bot['status']}")
        print(f"\n👤 Owner:")
        print(f"  User ID: {bot['user_id']}")
        print(f"  Username: {user['username']}")
        print(f"  Email: {user['email']}")
        print(f"\n📅 Timestamps:")
        print(f"  Created: {bot['created_at']}")
        print(f"  Last Active: {bot['last_active'] or 'Never'}")
        print(f"\n📝 Metadata: {bot['metadata']}")
        
        if data:
            print(f"\n📊 Data Summary:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"  • {key}: {len(value)} items")
                    elif isinstance(value, dict):
                        print(f"  • {key}: {len(value)} fields")
                    else:
                        print(f"  • {key}: {type(value).__name__}")
        
        print(f"\n{'='*70}\n")
    
    # ==================== STATISTICS ====================
    
    elif command == 'stats':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        
        # User stats
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1')
        active_users = cursor.fetchone()['count']
        
        # Bot stats
        cursor.execute('SELECT COUNT(*) as count FROM bots')
        bot_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bots WHERE status = 'online'")
        online_bots = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM bots WHERE status = 'offline'")
        offline_bots = cursor.fetchone()['count']
        
        # Session stats
        cursor.execute('SELECT COUNT(*) as count FROM sessions WHERE expires_at > CURRENT_TIMESTAMP')
        active_sessions = cursor.fetchone()['count']
        
        conn.close()
        
        avg_bots = bot_count / user_count if user_count > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"📊 System Statistics")
        print(f"{'='*70}\n")
        print(f"👥 USERS:")
        print(f"  Total: {user_count}")
        print(f"  Active: {active_users}")
        print(f"  Inactive: {user_count - active_users}")
        print(f"\n🤖 BOTS:")
        print(f"  Total: {bot_count}")
        print(f"  🟢 Online: {online_bots}")
        print(f"  🔴 Offline: {offline_bots}")
        print(f"  ⚪ Unknown: {bot_count - online_bots - offline_bots}")
        print(f"  📈 Average per User: {avg_bots:.2f}")
        print(f"\n🔑 SESSIONS:")
        print(f"  Active: {active_sessions}")
        print(f"\n{'='*70}\n")
    
    # ==================== CLEANUP ====================
    
    elif command == 'cleanup-sessions':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP')
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Cleaned up {deleted} expired session(s)")
    
    elif command == 'cleanup-resets':
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM password_resets WHERE used = 1 OR expires_at <= CURRENT_TIMESTAMP')
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Cleaned up {deleted} used/expired password reset(s)")
    
    # ==================== UNKNOWN ====================
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see available commands")

if __name__ == '__main__':
    main()