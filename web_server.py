"""
Web Server cho Bot Manager - Fix lỗi ngắt kết nối trên Mobile
Với tích hợp Authentication System (SQLite)
"""
# --- THÊM ĐOẠN NÀY ĐẦU TIÊN ---
import eventlet
eventlet.monkey_patch()
# ------------------------------

from flask import Flask, jsonify, request, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import os
from datetime import datetime
import queue
from collections import deque, defaultdict
import itertools
import uuid

# Import authentication module
from auth import AuthDB

# Configure Flask app với web folder
base_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(base_dir, 'web')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
CORS(app, supports_credentials=True)

# --- SỬA CẤU HÌNH SOCKETIO ---
# 1. Chuyển sang eventlet
# 2. Tăng ping_timeout lên 60s (để khi chuyển tab 1 lúc không bị disconnect ngay)
# 3. Tăng ping_interval lên 25s
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet', 
    ping_timeout=60, 
    ping_interval=25
)
# -----------------------------

# Initialize AuthDB
auth_db = AuthDB()

# Queue để relay log tới Socket.IO
log_queue = queue.Queue()
connected_clients = set()
bot_instances = {}
bot_data_store = defaultdict(dict)

# In-memory stores
MAX_LOGS = 500
MAX_MESSAGES = 500
MAX_COMMANDS_PER_BOT = 200
logs_storage = deque(maxlen=MAX_LOGS)
messages_storage = deque(maxlen=MAX_MESSAGES)
commands_by_bot = defaultdict(lambda: deque(maxlen=MAX_COMMANDS_PER_BOT))
commands_by_id = {}
commands_lock = threading.Lock()
command_counter = itertools.count(1)

def _current_time_iso():
    """Get current time in ISO format"""
    return datetime.utcnow().isoformat()

def _generate_command_id():
    """Generate unique command ID"""
    return f"cmd_{next(command_counter)}_{uuid.uuid4().hex[:6]}"

def _enqueue_command(bot_id, command_type, payload, source="api"):
    """Enqueue a command for bot execution"""
    command = {
        'id': _generate_command_id(),
        'bot_id': bot_id,
        'type': command_type,
        'payload': payload or {},
        'status': 'pending',
        'created_at': _current_time_iso(),
        'created_by': source
    }
    with commands_lock:
        commands_by_bot[bot_id].append(command)
        commands_by_id[command['id']] = command
    socketio.emit('new_command', command, namespace='/')
    return command

def emit_log_to_clients(log_data):
    """Emit log to all connected clients"""
    try:
        socketio.emit('new_log', log_data, namespace='/')
    except Exception as e:
        print(f'Error emitting log: {e}')

def emit_bot_update(bot_data):
    """Emit bot update to all connected clients"""
    try:
        socketio.emit('bot_update', bot_data, namespace='/')
    except Exception as e:
        print(f'Error emitting bot update: {e}')

def _emit_command_update(command):
    """Emit command update to clients"""
    socketio.emit('command_update', command, namespace='/')

def log_worker():
    """Background worker to process log queue"""
    while True:
        try:
            # Eventlet sleep để tránh block CPU 100% trong vòng lặp while True
            eventlet.sleep(0.1) 
            log_data = log_queue.get(timeout=1)
            if log_data:
                emit_log_to_clients(log_data)
        except queue.Empty:
            continue
        except Exception as e:
            print(f'Error in log worker: {e}')

def add_log(log_type, message, metadata=None, bot_id=None):
    """Add log entry to storage and queue"""
    log_data = {
        'type': log_type,
        'message': message,
        'timestamp': _current_time_iso(),
        'metadata': metadata or {},
        'bot_id': bot_id
    }
    logs_storage.append(log_data)
    log_queue.put(log_data)

class WebLogger:
    """Logger class for bot events"""
    
    @staticmethod
    def message(message_text, author_id, author_name, thread_id, thread_type, message_object=None):
        """Log a message event"""
        metadata = {
            'author_id': author_id,
            'author_name': author_name,
            'thread_id': thread_id,
            'thread_type': str(thread_type)
        }
        if message_object and isinstance(message_object, dict):
            metadata.update(message_object)
        elif message_object:
            metadata['message_object'] = str(message_object)
        add_log('message', message_text, metadata)

    @staticmethod
    def event(event_type, description, metadata=None):
        """Log a general event"""
        add_log('event', description, {
            'event_type': event_type,
            **(metadata or {})
        })

    @staticmethod
    def command(command_name, author_id, thread_id, success=True):
        """Log a command execution"""
        add_log('command', f'Command: {command_name}', {
            'command_name': command_name,
            'author_id': author_id,
            'thread_id': thread_id,
            'success': success
        })

    @staticmethod
    def error(error_message, exception=None):
        """Log an error"""
        add_log('error', error_message, {
            'exception': str(exception) if exception else None
        })

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Register new user"""
    data = request.get_json(silent=True) or {}
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    fullname = data.get('fullname', '').strip()
    
    # Validation
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    result = auth_db.create_user(username, email, password, fullname)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    add_log('event', f'New user registered: {username}', {'user_id': result['user_id']})
    return jsonify({'success': True, 'message': 'Registration successful'})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Login user"""
    data = request.get_json(silent=True) or {}
    
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username_or_email or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    
    result = auth_db.authenticate(username_or_email, password)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 401
    
    response = jsonify({
        'success': True,
        'user': result['user']
    })
    
    # Set session token in cookie
    response.set_cookie(
        'session_token', 
        result['session_token'], 
        max_age=7*24*60*60,  # 7 days
        httponly=True, 
        samesite='Lax'
    )
    
    add_log('event', f'User logged in: {result["user"]["username"]}', {'user_id': result['user']['id']})
    return response

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    session_token = request.cookies.get('session_token')
    
    if session_token:
        auth_db.logout(session_token)
        add_log('event', 'User logged out')
    
    response = jsonify({'success': True})
    response.set_cookie('session_token', '', expires=0)
    
    return response

@app.route('/api/auth/me', methods=['GET'])
def api_get_current_user():
    """Get current user info"""
    session_token = request.cookies.get('session_token')
    
    if not session_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = auth_db.validate_session(session_token)
    
    if not user:
        return jsonify({'error': 'Invalid session'}), 401
    
    return jsonify({'user': user})

@app.route('/api/auth/update-profile', methods=['POST'])
def api_update_profile():
    """Update user profile"""
    session_token = request.cookies.get('session_token')
    
    if not session_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = auth_db.validate_session(session_token)
    
    if not user:
        return jsonify({'error': 'Invalid session'}), 401
    
    data = request.get_json(silent=True) or {}
    
    result = auth_db.update_user(user['id'], **data)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    add_log('event', f'User profile updated: {user["username"]}', {'user_id': user['id']})
    return jsonify({'success': True})

@app.route('/api/auth/change-password', methods=['POST'])
def api_change_password():
    """Change user password"""
    session_token = request.cookies.get('session_token')
    
    if not session_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = auth_db.validate_session(session_token)
    
    if not user:
        return jsonify({'error': 'Invalid session'}), 401
    
    data = request.get_json(silent=True) or {}
    
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not old_password or not new_password:
        return jsonify({'error': 'Missing passwords'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    
    result = auth_db.change_password(user['id'], old_password, new_password)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # Clear session cookie
    response = jsonify({'success': True})
    response.set_cookie('session_token', '', expires=0)
    
    add_log('event', f'User password changed: {user["username"]}', {'user_id': user['id']})
    return response

@app.route('/api/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    """Request password reset"""
    data = request.get_json(silent=True) or {}
    
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    result = auth_db.create_password_reset_token(email)
    
    if not result['success']:
        # Don't reveal if email exists (security best practice)
        return jsonify({
            'success': True, 
            'message': 'If email exists, reset link will be sent'
        })
    
    # TODO: Send email with reset link
    # For now, print token to console (in production, send via email)
    print(f"Password reset token for {email}: {result['token']}")
    print(f"Reset URL: http://localhost:5000/reset-password?token={result['token']}")
    
    add_log('event', f'Password reset requested for email: {email}')
    return jsonify({
        'success': True, 
        'message': 'If email exists, reset link has been sent'
    })

@app.route('/api/auth/reset-password', methods=['POST'])
def api_reset_password():
    """Reset password using token"""
    data = request.get_json(silent=True) or {}
    
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '').strip()
    
    if not token or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    result = auth_db.reset_password(token, new_password)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    add_log('event', 'Password reset completed')
    return jsonify({'success': True})

@app.route('/api/auth/delete-account', methods=['POST'])
def api_delete_account():
    """Delete user account"""
    session_token = request.cookies.get('session_token')
    
    if not session_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = auth_db.validate_session(session_token)
    
    if not user:
        return jsonify({'error': 'Invalid session'}), 401
    
    data = request.get_json(silent=True) or {}
    password = data.get('password', '').strip()
    
    if not password:
        return jsonify({'error': 'Password required'}), 400
    
    # Verify password before deletion
    conn = auth_db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user['id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data or not auth_db.verify_password(password, user_data['password_hash']):
        return jsonify({'error': 'Incorrect password'}), 401
    
    username = user['username']
    auth_db.delete_user(user['id'])
    
    response = jsonify({'success': True})
    response.set_cookie('session_token', '', expires=0)
    
    add_log('event', f'User account deleted: {username}', {'user_id': user['id']})
    return response

# ==================== BOT MANAGEMENT ROUTES ====================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': _current_time_iso()})

@app.route('/api/bots', methods=['GET'])
def get_bots():
    """Get all bots"""
    return jsonify({'bots': list(bot_instances.values()), 'count': len(bot_instances)})

@app.route('/api/bots/register', methods=['POST'])
def api_register_bot():
    """Register a new bot"""
    payload = request.get_json(silent=True) or {}
    bot_id = payload.get('bot_id')
    
    if not bot_id:
        return jsonify({'error': 'bot_id is required'}), 400
    
    bot_instances[bot_id] = {
        'id': bot_id,
        'name': payload.get('name', bot_id),
        'status': payload.get('status', 'online'),
        'registered_at': _current_time_iso(),
        'metadata': payload.get('metadata', {})
    }
    
    emit_bot_update({'action': 'register', 'bot': bot_instances[bot_id]})
    add_log('event', f'Bot registered: {bot_id}', {'bot_id': bot_id})
    
    return jsonify({'status': 'ok', 'bot': bot_instances[bot_id]})

@app.route('/api/bot/<bot_id>/status', methods=['GET', 'POST'])
def bot_status(bot_id):
    """Get or update bot status"""
    if request.method == 'GET':
        if bot_id in bot_instances:
            return jsonify(bot_instances[bot_id])
        return jsonify({'error': 'Bot not found'}), 404

    # POST - Update status
    payload = request.get_json(silent=True) or {}
    status = payload.get('status', 'unknown')
    extra = payload.get('data', {})

    if bot_id not in bot_instances:
        bot_instances[bot_id] = {
            'id': bot_id,
            'name': extra.get('name', bot_id),
            'registered_at': _current_time_iso()
        }

    bot_instances[bot_id]['status'] = status
    bot_instances[bot_id]['last_update'] = _current_time_iso()
    bot_instances[bot_id].update(extra)

    event_payload = {
        'action': 'status_update',
        'bot_id': bot_id,
        'status': status,
        'data': extra
    }
    
    emit_bot_update(event_payload)
    add_log('event', f'Bot {bot_id} status: {status}', event_payload, bot_id=bot_id)
    
    return jsonify({'status': 'ok', 'bot': bot_instances[bot_id]})

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    """Get logs"""
    limit = int(request.args.get('limit', 100))
    logs = list(logs_storage)[-limit:]
    return jsonify({'logs': logs, 'count': len(logs)})

@app.route('/api/bot/<bot_id>/logs', methods=['POST'])
def api_post_logs(bot_id):
    """Post logs from bot"""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'error': 'Invalid payload'}), 400

    entries = payload if isinstance(payload, list) else [payload]
    for entry in entries:
        add_log(
            entry.get('type', 'info'), 
            entry.get('message', ''), 
            entry.get('metadata', {}), 
            bot_id=bot_id
        )

    return jsonify({'status': 'ok', 'received': len(entries)})

@app.route('/api/messages', methods=['GET'])
def api_get_messages():
    """Get messages"""
    limit = int(request.args.get('limit', 100))
    data = list(messages_storage)[-limit:]
    return jsonify({'messages': data, 'count': len(data)})

@app.route('/api/bot/<bot_id>/messages', methods=['POST'])
def api_post_messages(bot_id):
    """Post message from bot"""
    payload = request.get_json(silent=True) or {}
    
    message_entry = {
        'bot_id': bot_id,
        'message': payload.get('message'),
        'author_id': payload.get('author_id'),
        'author_name': payload.get('author_name'),
        'thread_id': payload.get('thread_id'),
        'thread_type': payload.get('thread_type'),
        'metadata': payload.get('metadata', {}),
        'timestamp': _current_time_iso()
    }
    
    messages_storage.append(message_entry)
    socketio.emit('new_message', message_entry, namespace='/')
    
    log_metadata = {
        'author_id': message_entry['author_id'],
        'author_name': message_entry['author_name'],
        'thread_id': message_entry['thread_id'],
        'thread_type': message_entry['thread_type'],
        **(message_entry.get('metadata') or {})
    }
    
    add_log('message', message_entry['message'], log_metadata, bot_id=bot_id)
    
    return jsonify({'status': 'ok'})

@app.route('/api/bot/<bot_id>/data', methods=['GET'])
def api_get_bot_data(bot_id):
    """Get bot data (groups, friends, etc.)"""
    if bot_id not in bot_data_store:
        return jsonify({'data': {}, 'updated_at': None}), 404
    return jsonify(bot_data_store[bot_id])

@app.route('/api/bot/<bot_id>/sync', methods=['POST'])
def api_sync_bot_data(bot_id):
    """Sync bot data"""
    payload = request.get_json(silent=True) or {}
    
    bot_data_store[bot_id] = {
        'data': payload,
        'updated_at': _current_time_iso()
    }
    
    bot_instances.setdefault(bot_id, {
        'id': bot_id,
        'name': payload.get('name', bot_id),
        'status': 'unknown',
        'registered_at': _current_time_iso()
    })
    
    add_log('event', f'Bot {bot_id} synced data', {
        'records': {
            'groups': len(payload.get('groups', []) or []),
            'friends': len(payload.get('friends', []) or []),
            'bot_id': bot_id
        }
    }, bot_id=bot_id)
    
    socketio.emit('bot_data_sync', {'bot_id': bot_id, 'data': payload}, namespace='/')
    
    return jsonify({'status': 'ok'})

@app.route('/api/commands', methods=['GET'])
def api_list_commands():
    """List all commands"""
    bot_id = request.args.get('bot_id')
    
    with commands_lock:
        if bot_id:
            commands = list(commands_by_bot.get(bot_id, []))
        else:
            commands = list(commands_by_id.values())
    
    return jsonify({'commands': commands, 'count': len(commands)})

@app.route('/api/commands', methods=['POST'])
def api_create_command():
    """Create a new command"""
    payload = request.get_json(silent=True) or {}
    bot_id = payload.get('bot_id')
    command_type = payload.get('type')
    
    if not bot_id or not command_type:
        return jsonify({'error': 'bot_id and type are required'}), 400
    
    command = _enqueue_command(bot_id, command_type, payload.get('payload', {}), source='api')
    
    return jsonify({'status': 'queued', 'command': command})

@app.route('/api/bot/<bot_id>/commands', methods=['GET'])
def api_get_commands(bot_id):
    """Get pending commands for bot"""
    limit = int(request.args.get('limit', 10))
    
    with commands_lock:
        pending = []
        for command in commands_by_bot.get(bot_id, []):
            if command['status'] == 'pending':
                command['status'] = 'dispatched'
                command['dispatched_at'] = _current_time_iso()
                pending.append(command)
            if len(pending) >= limit:
                break
    
    return jsonify({'commands': pending, 'count': len(pending)})

@app.route('/api/commands/<command_id>/ack', methods=['POST'])
def api_ack_command(command_id):
    """Acknowledge command completion"""
    payload = request.get_json(silent=True) or {}
    status = payload.get('status', 'completed')
    extra = payload.get('result', {})

    with commands_lock:
        command = commands_by_id.get(command_id)
        if not command:
            return jsonify({'error': 'Command not found'}), 404
        
        command['status'] = status
        command['result'] = extra
        command['completed_at'] = _current_time_iso()

    _emit_command_update(command)
    
    return jsonify({'status': 'ok', 'command': command})

# ==================== SOCKETIO HANDLERS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    print(f'✅ Client connected: {client_id}')
    
    socketio.emit('connection_established', {
        'status': 'connected',
        'client_id': client_id,
        'timestamp': _current_time_iso()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    connected_clients.discard(client_id)
    print(f'❌ Client disconnected: {client_id}')

@socketio.on('send_message')
def handle_send_message(data):
    """Handle send message request from client"""
    bot_id = data.get('bot_id')
    
    if not bot_id:
        socketio.emit('message_sent', {'status': 'error', 'error': 'bot_id required'})
        return

    payload = {
        'thread_id': data.get('thread_id'),
        'thread_type': data.get('thread_type', 'GROUP'),
        'message': data.get('message'),
        'attachments': data.get('attachments', []),
        'metadata': data.get('metadata', {})
    }
    
    command = _enqueue_command(bot_id, 'send_message', payload, source='socket')
    
    socketio.emit('message_sent', {
        'status': 'queued',
        'command_id': command['id'],
        'timestamp': _current_time_iso()
    })

# ==================== FILE SERVING ====================

@app.route('/')
def index():
    """Serve main index page"""
    index_path = os.path.join(web_dir, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    return "Web interface not found", 404

@app.route('/<path:subpath>')
def serve_web_pages(subpath):
    """Serve web pages and static files"""
    # Don't serve API routes
    if subpath.startswith('api/') or subpath.startswith('socket.io/'):
        return jsonify({'error': 'Not found'}), 404

    # Try to serve the file directly
    file_path = os.path.join(web_dir, subpath)
    if os.path.isfile(file_path):
        return send_file(file_path)

    # Try to serve index.html in subdirectory
    index_in_dir = os.path.join(web_dir, subpath, 'index.html')
    if os.path.isfile(index_in_dir):
        return send_file(index_in_dir)

    # Fall back to main index.html (for SPA routing)
    index_path = os.path.join(web_dir, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)

    return "Page not found", 404

# ==================== SERVER START ====================

def start_web_server(host='0.0.0.0', port=5000, debug=False):
    """Start the web server"""
    # Log worker thread giữ nguyên vì eventlet monkey_patch đã xử lý threading
    log_thread = threading.Thread(target=log_worker, daemon=True)
    log_thread.start()

    print(f'\n🌐 Starting Web Server with Eventlet...')
    print(f'📍 URL: http://{host}:{port}')
    print(f'📁 Serving files from: {web_dir}')
    print(f'🔐 Authentication: Enabled (SQLite)')
    print(f'💾 Database: data/users.db')
    print('=' * 50)

    # Create web directory if not exists
    os.makedirs(web_dir, exist_ok=True)

    try:
        # Eventlet sẽ tự động được sử dụng do async_mode='eventlet'
        socketio.run(app, host=host, port=port, debug=debug)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f'⚠️  Port {port} đã được sử dụng. Thử port khác...')
            try:
                socketio.run(app, host=host, port=port + 1, debug=debug)
            except Exception as e2:
                print(f'❌ Không thể khởi động web server: {e2}')
        else:
            print(f'❌ Lỗi khởi động web server: {e}')

# ==================== EXPORTS ====================

__all__ = [
    'start_web_server',
    'WebLogger',
    'add_log',
    'socketio',
    'app',
    'auth_db'
]

# ==================== MAIN ====================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        🤖 Bot Manager Web Server with Auth 🔐          ║
    ║                                                          ║
    ║  Features:                                              ║
    ║  ✅ Real-time Socket.IO communication                   ║
    ║  ✅ Bot management & monitoring                         ║
    ║  ✅ User authentication (SQLite)                        ║
    ║  ✅ Session management                                  ║
    ║  ✅ Profile management                                  ║
    ║  ✅ Password reset                                      ║
    ║  ✅ Responsive web interface                            ║
    ║                                                          ║
    ║  Created by: ere                                        ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Start server
    start_web_server(port=5000, debug=True)