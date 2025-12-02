# manage_bots.py
# -*- coding: utf-8 -*-
"""
Script quản lý bots từ command line
"""
from auth import AuthDB
import sys
import json

def print_help():
    """Print help message"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🤖 BOT MANAGEMENT COMMANDS                      ║
╚══════════════════════════════════════════════════════════════╝

📋 LIST BOTS:
  python manage_bots.py list <user_id>
    → Liệt kê tất cả bot của user
    
  python manage_bots.py all
    → Liệt kê tất cả bot trong hệ thống

➕ CREATE BOT:
  python manage_bots.py create <user_id> <bot_name>
    → Tạo bot mới cho user
    → Trả về Bot ID và Token (lưu lại!)

ℹ️  VIEW BOT INFO:
  python manage_bots.py info <bot_id>
    → Xem thông tin chi tiết bot
    
  python manage_bots.py data <bot_id>
    → Xem data của bot (groups, friends, etc.)
    
  python manage_bots.py token <bot_id> <user_id>
    → Xem token của bot (chỉ owner)

✏️  UPDATE BOT:
  python manage_bots.py rename <bot_id> <user_id> <new_name>
    → Đổi tên bot
    
  python manage_bots.py regen-token <bot_id> <user_id>
    → Tạo lại token mới

🗑️  DELETE BOT:
  python manage_bots.py delete <bot_id> <user_id>
    → Xóa bot (cần xác nhận)

📊 STATISTICS:
  python manage_bots.py stats <user_id>
    → Thống kê bot của user
    
  python manage_bots.py global-stats
    → Thống kê toàn hệ thống

═══════════════════════════════════════════════════════════════
""")

def main():
    auth_db = AuthDB()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    # ==================== LIST COMMANDS ====================
    
    if command == 'list':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_bots.py list <user_id>")
            return
        
        user_id = int(sys.argv[2])
        
        # Check if user exists
        user = auth_db.get_user_by_id(user_id)
        if not user:
            print(f"❌ User ID {user_id} not found")
            return
        
        bots = auth_db.get_user_bots(user_id)
        
        print(f"\n{'='*70}")
        print(f"🤖 Bots của {user['username']} (ID: {user_id})")
        print(f"{'='*70}\n")
        
        if not bots:
            print("📭 Không có bot nào.")
            return
        
        for i, bot in enumerate(bots, 1):
            print(f"[{i}] Bot ID: {bot['id']}")
            print(f"    Name: {bot['name']}")
            print(f"    Status: {bot['status']}")
            print(f"    Token: {bot['token'][:20]}...{bot['token'][-10:]}" if bot['token'] else "    No token")
            print(f"    Created: {bot['created_at']}")
            print(f"    Last Active: {bot['last_active'] or 'Never'}")
            print(f"    {'-'*66}")
        
        print(f"\n📊 Total: {len(bots)} bot(s)")
    
    # ==================== CREATE COMMAND ====================
    
    elif command == 'create':
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_bots.py create <user_id> <bot_name>")
            return
        
        user_id = int(sys.argv[2])
        bot_name = ' '.join(sys.argv[3:])  # Allow bot names with spaces
        
        # Check if user exists
        user = auth_db.get_user_by_id(user_id)
        if not user:
            print(f"❌ User ID {user_id} not found")
            return
        
        print(f"\n🔄 Creating bot '{bot_name}' for {user['username']}...")
        
        result = auth_db.create_bot(user_id, bot_name)
        
        if result['success']:
            print(f"\n{'='*70}")
            print(f"✅ Bot created successfully!")
            print(f"{'='*70}")
            print(f"\n📋 Bot Information:")
            print(f"   Bot ID: {result['bot_id']}")
            print(f"   Name: {bot_name}")
            print(f"   Owner: {user['username']} (ID: {user_id})")
            print(f"\n🔑 Authentication Token:")
            print(f"   {result['token']}")
            print(f"\n⚠️  IMPORTANT: Save this token! It won't be shown again.")
            print(f"   You can use 'regen-token' command to generate a new one.\n")
            print(f"{'='*70}\n")
        else:
            print(f"❌ Error: {result['error']}")
    
    # ==================== INFO COMMAND ====================
    
    elif command == 'info':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_bots.py info <bot_id>")
            return
        
        bot_id = sys.argv[2]
        bot = auth_db.get_bot(bot_id)
        
        if not bot:
            print(f"❌ Bot {bot_id} not found")
            return
        
        # Get owner info
        user = auth_db.get_user_by_id(bot['user_id'])
        
        print(f"\n{'='*70}")
        print(f"🤖 Bot Information")
        print(f"{'='*70}\n")
        print(f"ID: {bot['id']}")
        print(f"Name: {bot['name']}")
        print(f"Status: {bot['status']}")
        print(f"\n👤 Owner:")
        print(f"   User ID: {bot['user_id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"\n📅 Timestamps:")
        print(f"   Created: {bot['created_at']}")
        print(f"   Last Active: {bot['last_active'] or 'Never'}")
        print(f"\n📝 Metadata:")
        print(f"   {bot['metadata']}")
        
        # Show data summary
        data = auth_db.get_bot_data(bot_id)
        if data:
            print(f"\n📊 Data Summary:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"   • {key}: {len(value)} items")
                    elif isinstance(value, dict):
                        print(f"   • {key}: {len(value)} fields")
                    else:
                        print(f"   • {key}: {type(value).__name__}")
        else:
            print(f"\n📊 Data: No data synced yet")
        
        print(f"\n{'='*70}\n")
    
    # ==================== DATA COMMAND ====================
    
    elif command == 'data':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_bots.py data <bot_id>")
            return
        
        bot_id = sys.argv[2]
        data = auth_db.get_bot_data(bot_id)
        
        if not data:
            print(f"❌ No data found for bot {bot_id}")
            return
        
        print(f"\n{'='*70}")
        print(f"📊 Bot Data for {bot_id}")
        print(f"{'='*70}\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
    
    # ==================== DELETE COMMAND ====================
    
    elif command == 'delete':
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_bots.py delete <bot_id> <user_id>")
            return
        
        bot_id = sys.argv[2]
        user_id = int(sys.argv[3])
        
        # Get bot info
        bot = auth_db.get_bot(bot_id)
        if not bot:
            print(f"❌ Bot {bot_id} not found")
            return
        
        print(f"\n⚠️  WARNING: You are about to delete bot '{bot['name']}' (ID: {bot_id})")
        print(f"This action CANNOT be undone!")
        confirm = input(f"\nType 'yes' to confirm deletion: ")
        
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        result = auth_db.delete_bot(bot_id, user_id)
        
        if result['success']:
            print(f"✅ Bot {bot_id} deleted successfully")
        else:
            print(f"❌ Error: {result['error']}")
    
    # ==================== ALL COMMAND ====================
    
    elif command == 'all':
        bots = auth_db.get_all_bots()
        
        print(f"\n{'='*70}")
        print(f"🤖 All Bots in System")
        print(f"{'='*70}\n")
        
        if not bots:
            print("📭 No bots in system.")
            return
        
        for i, bot in enumerate(bots, 1):
            print(f"[{i}] {bot['id']} - {bot['name']}")
            print(f"    Owner: {bot['username']} ({bot['email']})")
            print(f"    Status: {bot['status']}")
            print(f"    Created: {bot['created_at']}")
            print(f"    Last Active: {bot['last_active'] or 'Never'}")
            print(f"    {'-'*66}")
        
        print(f"\n📊 Total: {len(bots)} bot(s)")
    
    # ==================== TOKEN COMMAND ====================
    
    elif command == 'token':
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_bots.py token <bot_id> <user_id>")
            return
        
        bot_id = sys.argv[2]
        user_id = int(sys.argv[3])
        
        token = auth_db.get_bot_token(bot_id, user_id)
        
        if token:
            print(f"\n🔑 Bot Token for {bot_id}:")
            print(f"   {token}\n")
        else:
            print(f"❌ Cannot get token. Either bot doesn't exist or you're not the owner.")
    
    # ==================== RENAME COMMAND ====================
    
    elif command == 'rename':
        if len(sys.argv) < 5:
            print("❌ Usage: python manage_bots.py rename <bot_id> <user_id> <new_name>")
            return
        
        bot_id = sys.argv[2]
        user_id = int(sys.argv[3])
        new_name = ' '.join(sys.argv[4:])
        
        result = auth_db.update_bot_info(bot_id, user_id, name=new_name)
        
        if result['success']:
            print(f"✅ Bot {bot_id} renamed to '{new_name}'")
        else:
            print(f"❌ Error: {result['error']}")
    
    # ==================== REGEN-TOKEN COMMAND ====================
    
    elif command == 'regen-token':
        if len(sys.argv) < 4:
            print("❌ Usage: python manage_bots.py regen-token <bot_id> <user_id>")
            return
        
        bot_id = sys.argv[2]
        user_id = int(sys.argv[3])
        
        print(f"\n⚠️  WARNING: Regenerating token will invalidate the old token!")
        confirm = input(f"Type 'yes' to confirm: ")
        
        if confirm.lower() != 'yes':
            print("❌ Cancelled.")
            return
        
        result = auth_db.regenerate_bot_token(bot_id, user_id)
        
        if result['success']:
            print(f"\n✅ New token generated successfully!")
            print(f"🔑 New Token:")
            print(f"   {result['token']}\n")
        else:
            print(f"❌ Error: {result['error']}")
    
    # ==================== STATS COMMAND ====================
    
    elif command == 'stats':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_bots.py stats <user_id>")
            return
        
        user_id = int(sys.argv[2])
        user = auth_db.get_user_by_id(user_id)
        
        if not user:
            print(f"❌ User ID {user_id} not found")
            return
        
        bots = auth_db.get_user_bots(user_id)
        
        online = sum(1 for bot in bots if bot['status'] == 'online')
        offline = sum(1 for bot in bots if bot['status'] == 'offline')
        unknown = sum(1 for bot in bots if bot['status'] not in ['online', 'offline'])
        
        print(f"\n{'='*70}")
        print(f"📊 Statistics for {user['username']}")
        print(f"{'='*70}\n")
        print(f"Total Bots: {len(bots)}")
        print(f"  🟢 Online: {online}")
        print(f"  🔴 Offline: {offline}")
        print(f"  ⚪ Unknown: {unknown}")
        print()
    
    # ==================== GLOBAL-STATS COMMAND ====================
    
    elif command == 'global-stats':
        bots = auth_db.get_all_bots()
        
        conn = auth_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        conn.close()
        
        online = sum(1 for bot in bots if bot['status'] == 'online')
        offline = sum(1 for bot in bots if bot['status'] == 'offline')
        unknown = sum(1 for bot in bots if bot['status'] not in ['online', 'offline'])
        
        # Count bots per user
        user_bot_count = {}
        for bot in bots:
            user_bot_count[bot['user_id']] = user_bot_count.get(bot['user_id'], 0) + 1
        
        avg_bots = len(bots) / user_count if user_count > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"📊 Global System Statistics")
        print(f"{'='*70}\n")
        print(f"👥 Total Users: {user_count}")
        print(f"🤖 Total Bots: {len(bots)}")
        print(f"📈 Average Bots per User: {avg_bots:.2f}")
        print(f"\n🚦 Bot Status:")
        print(f"  🟢 Online: {online}")
        print(f"  🔴 Offline: {offline}")
        print(f"  ⚪ Unknown: {unknown}")
        print()
    
    # ==================== UNKNOWN COMMAND ====================
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see available commands")

if __name__ == '__main__':
    main()