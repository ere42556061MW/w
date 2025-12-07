"""
Web Server cho Bot Manager - Fix lỗi ngắt kết nối trên Mobile
Với tích hợp Authentication System & Bot Ownership Management (SQLite)
"""
# --- CHỌN MỘT TRONG HAI ---
# Option 1: Dùng gevent (khuyến nghị cho Python 3.12+)
from gevent import monkey
monkey.patch_all()

# Option 2: Dùng threading (không cần eventlet/gevent)
# Bỏ comment dòng dưới nếu không muốn dùng async mode
# pass

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
from functools import wraps

# Import authentication module
from auth import AuthDB

# Configure Flask app với web folder
base_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(base_dir, 'web')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
CORS(app, supports_credentials=True)

# --- SỬA CẤU HÌNH SOCKETIO ---
# Chọn async_mode phù hợp với environment của bạn
# - 'gevent': Tốt nhất cho production, Python 3.12+
# - 'threading': Không cần cài thêm gì, ổn định
# - 'eventlet': Cho Python < 3.12
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='gevent',  # Đổi thành 'threading' nếu không dùng gevent
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
            # Sleep để tránh block CPU 100% trong vòng lặp while True
            import time
            time.sleep(0.1) 
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

# ==================== AUTHENTICATION DECORATOR ====================

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.cookies.get('session_token')
        
        if not session_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = auth_db.validate_session(session_token)
        
        if not user:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Pass user to the route function
        return f(user, *args, **kwargs)
    
    return decorated_function

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

# ==================== BOT OWNERSHIP ROUTES ====================

@app.route('/api/my-bots', methods=['GET'])
@require_auth
def api_get_my_bots(user):
    """Get all bots owned by current user"""
    bots = auth_db.get_user_bots(user['id'])
    return jsonify({'bots': bots, 'count': len(bots)})

@app.route('/api/my-bots', methods=['POST'])
@require_auth
def api_create_my_bot(user):
    """Create a new bot"""
    data = request.get_json(silent=True) or {}
    
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Bot name is required'}), 400
    
    metadata = data.get('metadata', {})
    
    result = auth_db.create_bot(user['id'], name, metadata)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    add_log('event', f'New bot created: {result["bot_id"]}', {
        'bot_id': result['bot_id'],
        'user_id': user['id']
    })
    
    return jsonify({
        'success': True,
        'bot_id': result['bot_id'],
        'token': result['token']
    })

@app.route('/api/my-bots/<bot_id>', methods=['GET'])
@require_auth
def api_get_my_bot(user, bot_id):
    """Get specific bot details"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id):
        return jsonify({'error': 'Not authorized'}), 403
    
    bot = auth_db.get_bot(bot_id)
    
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    return jsonify({'bot': bot})

@app.route('/api/my-bots/<bot_id>', methods=['PUT'])
@require_auth
def api_update_my_bot(user, bot_id):
    """Update bot info"""
    data = request.get_json(silent=True) or {}
    
    result = auth_db.update_bot_info(bot_id, user['id'], **data)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    add_log('event', f'Bot updated: {bot_id}', {'bot_id': bot_id, 'user_id': user['id']})
    
    return jsonify({'success': True})

@app.route('/api/my-bots/<bot_id>', methods=['DELETE'])
@require_auth
def api_delete_my_bot(user, bot_id):
    """Delete a bot"""
    result = auth_db.delete_bot(bot_id, user['id'])
    
    if not result['success']:
        return jsonify({'error': result['error']}), 403
    
    add_log('event', f'Bot deleted: {bot_id}', {'bot_id': bot_id, 'user_id': user['id']})
    
    return jsonify({'success': True})

@app.route('/api/my-bots/<bot_id>/data', methods=['GET'])
@require_auth
def api_get_my_bot_data(user, bot_id):
    """Get bot data"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id):
        return jsonify({'error': 'Not authorized'}), 403
    
    data = auth_db.get_bot_data(bot_id)
    
    if data is None:
        return jsonify({'data': None})
    
    return jsonify({'data': data})

@app.route('/api/my-bots/<bot_id>/token', methods=['GET'])
@require_auth
def api_get_my_bot_token(user, bot_id):
    """Get bot token"""
    token = auth_db.get_bot_token(bot_id, user['id'])
    
    if not token:
        return jsonify({'error': 'Not authorized or bot not found'}), 403
    
    return jsonify({'token': token})

@app.route('/api/my-bots/<bot_id>/regenerate-token', methods=['POST'])
@require_auth
def api_regenerate_my_bot_token(user, bot_id):
    """Regenerate bot token"""
    result = auth_db.regenerate_bot_token(bot_id, user['id'])
    
    if not result['success']:
        return jsonify({'error': result['error']}), 403
    
    add_log('event', f'Bot token regenerated: {bot_id}', {'bot_id': bot_id, 'user_id': user['id']})
    
    return jsonify({'success': True, 'token': result['token']})

# ==================== BOT API ROUTES (For bot clients) ====================

@app.route('/api/bot/auth', methods=['POST'])
def api_bot_auth():
    """Authenticate bot using token"""
    data = request.get_json(silent=True) or {}
    
    bot_id = data.get('bot_id', '').strip()
    token = data.get('token', '').strip()
    
    if not bot_id or not token:
        return jsonify({'error': 'bot_id and token required'}), 400
    
    if not auth_db.verify_bot_token(bot_id, token):
        return jsonify({'error': 'Invalid bot credentials'}), 401
    
    bot = auth_db.get_bot(bot_id)
    
    return jsonify({
        'success': True,
        'bot': bot
    })

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
        bot = auth_db.get_bot(bot_id)
        if bot:
            return jsonify(bot)
        
        # Fallback to old in-memory system
        if bot_id in bot_instances:
            return jsonify(bot_instances[bot_id])
        return jsonify({'error': 'Bot not found'}), 404

    # POST - Update status (requires bot token)
    payload = request.get_json(silent=True) or {}
    token = payload.get('token') or request.headers.get('X-Bot-Token')
    
    # Verify bot token if provided
    if token and not auth_db.verify_bot_token(bot_id, token):
        return jsonify({'error': 'Invalid bot token'}), 401
    
    status = payload.get('status', 'unknown')
    extra = payload.get('data', {})

    # Update in database if bot exists
    bot = auth_db.get_bot(bot_id)
    if bot:
        auth_db.update_bot_status(bot_id, status)
    
    # Also update in-memory for backward compatibility
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
    # Try database first
    data = auth_db.get_bot_data(bot_id)
    if data:
        return jsonify({'data': data, 'source': 'database'})
    
    # Fallback to in-memory store
    if bot_id not in bot_data_store:
        return jsonify({'data': {}, 'updated_at': None}), 404
    
    return jsonify({**bot_data_store[bot_id], 'source': 'memory'})

@app.route('/api/bot/<bot_id>/sync', methods=['POST'])
def api_sync_bot_data(bot_id):
    """Sync bot data"""
    payload = request.get_json(silent=True) or {}
    token = payload.get('token') or request.headers.get('X-Bot-Token')
    
    # Verify bot token if provided
    if token and not auth_db.verify_bot_token(bot_id, token):
        return jsonify({'error': 'Invalid bot token'}), 401
    
    # Save to database if bot exists
    bot = auth_db.get_bot(bot_id)
    if bot:
        auth_db.update_bot_data(bot_id, payload)
    
    # Also save to in-memory store for backward compatibility
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

# ==================== USER MANAGEMENT APIS ====================

@app.route('/api/users', methods=['GET'])
@require_auth
def api_get_users(user):
    """Get all users (admin only)"""
    # Check if user is admin
    if user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = auth_db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, fullname, created_at, role FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'users': users, 'count': len(users)})

@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def api_get_user(user, user_id):
    """Get user details"""
    # Users can only view their own profile or admins can view any
    if user['id'] != user_id and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    target_user = auth_db.get_user_by_id(user_id)
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': target_user})

@app.route('/api/users/<int:user_id>/bots', methods=['GET'])
@require_auth
def api_get_user_bots(user, user_id):
    """Get all bots of a user"""
    if user['id'] != user_id and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    bots = auth_db.get_user_bots(user_id)
    return jsonify({'bots': bots, 'count': len(bots)})

@app.route('/api/users/search', methods=['GET'])
@require_auth
def api_search_users(user):
    """Search users by username or email"""
    if user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Search query too short'}), 400
    
    conn = auth_db.get_connection()
    cursor = conn.cursor()
    search_pattern = f'%{query}%'
    cursor.execute(
        'SELECT id, username, email, fullname, created_at FROM users WHERE username LIKE ? OR email LIKE ? LIMIT 20',
        (search_pattern, search_pattern)
    )
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'users': users, 'count': len(users)})

# ==================== BOT MANAGEMENT APIS ====================

@app.route('/api/admin/bots', methods=['GET'])
@require_auth
def api_admin_get_all_bots(user):
    """Get all bots (admin only)"""
    if user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    bots = auth_db.get_all_bots()
    return jsonify({'bots': bots, 'count': len(bots)})

@app.route('/api/bot/<bot_id>/info', methods=['GET'])
@require_auth
def api_get_bot_info(user, bot_id):
    """Get detailed bot information"""
    # Only owner or admin can view
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    bot = auth_db.get_bot(bot_id)
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Get bot stats
    with commands_lock:
        bot_commands = list(commands_by_bot.get(bot_id, []))
    
    stats = {
        'total_commands': len(bot_commands),
        'pending_commands': len([c for c in bot_commands if c['status'] == 'pending']),
        'completed_commands': len([c for c in bot_commands if c['status'] == 'completed']),
        'failed_commands': len([c for c in bot_commands if c['status'] == 'failed'])
    }
    
    return jsonify({
        'bot': bot,
        'stats': stats,
        'online': bot.get('status') == 'online'
    })

@app.route('/api/bot/<bot_id>/commands-history', methods=['GET'])
@require_auth
def api_get_bot_commands_history(user, bot_id):
    """Get bot command execution history"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    limit = int(request.args.get('limit', 50))
    
    with commands_lock:
        commands = list(commands_by_bot.get(bot_id, []))[-limit:]
    
    return jsonify({'commands': commands, 'count': len(commands)})

@app.route('/api/bot/<bot_id>/send-command', methods=['POST'])
@require_auth
def api_send_bot_command(user, bot_id):
    """Send a command to bot"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    payload = request.get_json(silent=True) or {}
    
    command_type = payload.get('type')
    command_payload = payload.get('payload', {})
    
    if not command_type:
        return jsonify({'error': 'Command type is required'}), 400
    
    command = _enqueue_command(bot_id, command_type, command_payload, source='api')
    
    add_log('event', f'Command sent to bot: {command_type}', {
        'bot_id': bot_id,
        'command_id': command['id'],
        'command_type': command_type
    })
    
    return jsonify({'status': 'ok', 'command': command})

@app.route('/api/bot/<bot_id>/restart', methods=['POST'])
@require_auth
def api_restart_bot(user, bot_id):
    """Send restart command to bot"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    command = _enqueue_command(bot_id, 'restart', {}, source='api')
    
    add_log('event', f'Bot restart requested: {bot_id}', {'bot_id': bot_id})
    
    return jsonify({'status': 'ok', 'command': command})

@app.route('/api/bot/<bot_id>/stop', methods=['POST'])
@require_auth
def api_stop_bot(user, bot_id):
    """Send stop command to bot"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    command = _enqueue_command(bot_id, 'stop', {}, source='api')
    
    add_log('event', f'Bot stop requested: {bot_id}', {'bot_id': bot_id})
    
    return jsonify({'status': 'ok', 'command': command})

@app.route('/api/bot/<bot_id>/settings', methods=['GET', 'PUT'])
@require_auth
def api_bot_settings(user, bot_id):
    """Get or update bot settings"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    bot = auth_db.get_bot(bot_id)
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    if request.method == 'GET':
        return jsonify({'settings': bot.get('metadata', {})})
    
    # PUT - Update settings
    payload = request.get_json(silent=True) or {}
    
    result = auth_db.update_bot_info(bot_id, user['id'], metadata=payload)
    
    if not result['success']:
        return jsonify({'error': result.get('error', 'Update failed')}), 400
    
    add_log('event', f'Bot settings updated: {bot_id}', {'bot_id': bot_id})
    
    return jsonify({'success': True, 'settings': payload})

# ==================== STATISTICS & ANALYTICS APIS ====================

@app.route('/api/stats/overview', methods=['GET'])
@require_auth
def api_stats_overview(user):
    """Get overview statistics"""
    conn = auth_db.get_connection()
    cursor = conn.cursor()
    
    # Count users
    cursor.execute('SELECT COUNT(*) as count FROM users')
    total_users = cursor.fetchone()['count']
    
    # Count bots
    cursor.execute('SELECT COUNT(*) as count FROM bots')
    total_bots = cursor.fetchone()['count']
    
    # Count user bots
    cursor.execute('SELECT COUNT(*) as count FROM bots WHERE user_id = ?', (user['id'],))
    user_bots = cursor.fetchone()['count']
    
    conn.close()
    
    with commands_lock:
        total_commands = len(commands_by_id)
        pending_commands = len([c for c in commands_by_id.values() if c['status'] == 'pending'])
    
    return jsonify({
        'total_users': total_users,
        'total_bots': total_bots,
        'user_bots': user_bots,
        'total_commands': total_commands,
        'pending_commands': pending_commands,
        'total_logs': len(logs_storage),
        'total_messages': len(messages_storage),
        'connected_clients': len(connected_clients)
    })

@app.route('/api/stats/bot/<bot_id>', methods=['GET'])
@require_auth
def api_stats_bot(user, bot_id):
    """Get bot statistics"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    with commands_lock:
        bot_commands = list(commands_by_bot.get(bot_id, []))
    
    # Count logs
    bot_logs = [log for log in logs_storage if log.get('bot_id') == bot_id]
    
    # Count messages
    bot_messages = [msg for msg in messages_storage if msg.get('bot_id') == bot_id]
    
    stats = {
        'total_commands': len(bot_commands),
        'pending_commands': len([c for c in bot_commands if c['status'] == 'pending']),
        'completed_commands': len([c for c in bot_commands if c['status'] == 'completed']),
        'failed_commands': len([c for c in bot_commands if c['status'] == 'failed']),
        'total_logs': len(bot_logs),
        'total_messages': len(bot_messages),
        'command_types': {}
    }
    
    # Count by command type
    for cmd in bot_commands:
        cmd_type = cmd['type']
        stats['command_types'][cmd_type] = stats['command_types'].get(cmd_type, 0) + 1
    
    return jsonify(stats)

# ==================== DATA EXPORT APIS ====================

@app.route('/api/export/logs', methods=['GET'])
@require_auth
def api_export_logs(user):
    """Export logs as JSON"""
    bot_id = request.args.get('bot_id')
    limit = int(request.args.get('limit', 1000))
    
    if bot_id:
        # Check authorization
        if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
            return jsonify({'error': 'Not authorized'}), 403
        
        logs = [log for log in logs_storage if log.get('bot_id') == bot_id]
    else:
        logs = list(logs_storage)
    
    logs = logs[-limit:]
    
    return jsonify({
        'exported_at': _current_time_iso(),
        'count': len(logs),
        'logs': logs
    })

@app.route('/api/export/messages', methods=['GET'])
@require_auth
def api_export_messages(user):
    """Export messages as JSON"""
    bot_id = request.args.get('bot_id')
    limit = int(request.args.get('limit', 1000))
    
    if bot_id:
        # Check authorization
        if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
            return jsonify({'error': 'Not authorized'}), 403
        
        messages = [msg for msg in messages_storage if msg.get('bot_id') == bot_id]
    else:
        messages = list(messages_storage)
    
    messages = messages[-limit:]
    
    return jsonify({
        'exported_at': _current_time_iso(),
        'count': len(messages),
        'messages': messages
    })

@app.route('/api/export/bot-data/<bot_id>', methods=['GET'])
@require_auth
def api_export_bot_data(user, bot_id):
    """Export bot data"""
    if not auth_db.verify_bot_ownership(user['id'], bot_id) and user.get('role') != 'admin':
        return jsonify({'error': 'Not authorized'}), 403
    
    bot = auth_db.get_bot(bot_id)
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    bot_data = auth_db.get_bot_data(bot_id)
    
    with commands_lock:
        commands = list(commands_by_bot.get(bot_id, []))
    
    logs = [log for log in logs_storage if log.get('bot_id') == bot_id]
    messages = [msg for msg in messages_storage if msg.get('bot_id') == bot_id]
    
    return jsonify({
        'exported_at': _current_time_iso(),
        'bot': bot,
        'data': bot_data,
        'commands': commands,
        'logs': list(logs),
        'messages': list(messages)
    })

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
    # Log worker thread
    log_thread = threading.Thread(target=log_worker, daemon=True)
    log_thread.start()

    print(f'\n🌐 Starting Web Server...')
    print(f'🔗 URL: http://{host}:{port}')
    print(f'📁 Serving files from: {web_dir}')
    print(f'🔐 Authentication: Enabled (SQLite)')
    print(f'💾 Database: data/users.db')
    print(f'🤖 Bot Management: Enabled')
    print('=' * 50)

    # Create web directory if not exists
    os.makedirs(web_dir, exist_ok=True)

    try:
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
    ║  ✅ Bot ownership & access control                      ║
    ║  ✅ Session management                                  ║
    ║  ✅ Profile management                                  ║
    ║  ✅ Password reset                                      ║
    ║  ✅ Bot token authentication                            ║
    ║  ✅ Responsive web interface                            ║
    ║                                                          ║
    ║  Created by: ere                                        ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Start server
    start_web_server(port=5000, debug=True)