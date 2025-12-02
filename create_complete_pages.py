# -*- coding: utf-8 -*-
"""
Create complete HTML page files with proper content structure
"""

from pathlib import Path

# Read home template
home_path = Path('web/home/index.html')
with open(home_path, 'r', encoding='utf-8') as f:
    home_template = f.read()

# Extract sidebar and footer
import re
sidebar_match = re.search(r'(<!-- Sidebar Navigation -->.*?</div>)\s*<section', home_template, re.DOTALL)
sidebar = sidebar_match.group(1) if sidebar_match else ""

footer_match = re.search(r'(</section>.*)', home_template, re.DOTALL)
footer = footer_match.group(1) if footer_match else ""

# Define pages with their specific content
pages_html = {
    'manager': '''<div class="page manager-page active" id="manager-page">
<div class="container">
<!-- Phần 1: Danh sách -->
<div class="panel list-panel">
<div class="panel-header"><span>Danh sách</span></div>
<div class="panel-content">
<div class="tabs">
<button class="tab active" data-tab="groups">Nhóm</button>
<button class="tab" data-tab="friends">Bạn bè</button>
</div>
<div id="groups-list" class="list-content"></div>
<div id="friends-list" class="list-content" style="display: none;"></div>
</div>
</div>
<!-- Phần 2: Log & Composer -->
<div class="panel log-panel">
<div class="panel-header">
<span>Log Tin Nhắn & Events</span>
<span class="badge" id="log-count">0</span>
</div>
<div class="log-messages" id="log-content">
<div class="log-entry">
<div class="log-box">
<div class="log-header">
<div>Tin nhắn mới <span class="message-count">#1</span></div>
<span class="account-badge">Acc 1</span>
</div>
<div class="log-content-area">
<div class="log-row"><span class="log-icon">📨</span><span class="log-label">Message:</span><span class="log-value">Bot đã sẵn sàng nhận lệnh</span></div>
<div class="log-row"><span class="log-icon">👤</span><span class="log-label">User:</span><span class="log-value">Bot System</span></div>
</div>
</div>
</div>
</div>
<!-- Message Composer -->
<div class="message-composer" id="message-composer">
<div class="composer-input-group">
<textarea class="composer-textarea" id="composer-textarea" placeholder="Nhập tin nhắn..." rows="1"></textarea>
<button class="composer-send-btn" id="composer-send-btn">Gửi</button>
</div>
<div class="composer-options">
<div class="composer-option"><span>TTL:</span><input type="number" id="composer-ttl" value="0" min="0" step="1000" placeholder="0ms"></div>
<div class="composer-option"><button id="composer-send-all">Gửi tất cả</button></div>
<div class="composer-option"><button id="composer-run-cmd">Gửi Lệnh</button></div>
</div>
</div>
</div>
</div>
</div>''',

    'bots': '''<div class="page active" id="bots-page">
<div class="bots-management-container">
<div class="bots-management-card">
<h2 class="bots-management-title">🤖 Quản Lý Bot</h2>
<div class="bot-controls">
<button class="control-btn-large start-all" id="start-all-bots">▶️ Khởi động tất cả Bot</button>
<button class="control-btn-large stop-all" id="stop-all-bots">⏹️ Dừng tất cả Bot</button>
</div>
<div id="bots-management-list"></div>
<button class="btn btn-primary" id="add-new-bot" style="margin-top: 20px;">➕ Thêm Bot Mới</button>
</div>
</div>
</div>''',

    'create': '''<div class="page active" id="create-page">
<div class="home-container">
<div class="create-card">
<h2 class="create-title">➕ Tạo Bot Mới</h2>
<p style="text-align: center; color: #6b7280; margin-bottom: 30px;">Cấu hình bot của bạn</p>
<div class="action-group">
<label>Tên Bot:</label>
<input type="text" class="input-field" id="bot-name" placeholder="Ví dụ: Bot Zalo">
</div>
<div class="action-group">
<label>Token:</label>
<input type="password" class="input-field" id="bot-token" placeholder="Nhập token...">
</div>
<div class="action-group">
<label>Mô tả:</label>
<textarea class="input-field" id="bot-description" placeholder="Mô tả bot..." rows="3"></textarea>
</div>
<button class="btn btn-primary" id="create-bot-btn">Tạo Bot</button>
</div>
</div>
</div>''',

    'rental': '''<div class="page active" id="rental-page">
<div class="home-container">
<div class="rental-container">
<h2 class="page-title">💰 Cho Thuê Bot</h2>
<div class="rental-list" id="rental-list"></div>
<button class="btn btn-primary" id="add-rental-btn" style="margin-top: 20px;">➕ Thêm Gói Cho Thuê</button>
</div>
</div>
</div>''',

    'payment': '''<div class="page active" id="payment-page">
<div class="home-container">
<div class="payment-container">
<h2 class="page-title">💳 Thanh Toán</h2>
<div class="payment-list" id="payment-list"></div>
</div>
</div>
</div>''',

    'commands': '''<div class="page active" id="commands-page">
<div class="home-container">
<div class="commands-container">
<h2 class="page-title">📋 Danh Sách Lệnh</h2>
<div class="commands-list" id="commands-list"></div>
<button class="btn btn-primary" id="add-command-btn" style="margin-top: 20px;">➕ Thêm Lệnh</button>
</div>
</div>
</div>''',

    'statistics': '''<div class="page active" id="statistics-page">
<div class="home-container">
<div class="statistics-container">
<h2 class="page-title">📊 Thống Kê</h2>
<div class="stats-grid">
<div class="stat-card"><h3>Tin Nhắn</h3><p id="stat-messages">0</p></div>
<div class="stat-card"><h3>Người Dùng</h3><p id="stat-users">0</p></div>
<div class="stat-card"><h3>Bot Hoạt Động</h3><p id="stat-active-bots">0</p></div>
<div class="stat-card"><h3>Lệnh Xử Lý</h3><p id="stat-commands">0</p></div>
</div>
</div>
</div>
</div>''',

    'users': '''<div class="page active" id="users-page">
<div class="home-container">
<div class="users-container">
<h2 class="page-title">👥 Quản Lý Người Dùng</h2>
<div class="users-list" id="users-list"></div>
</div>
</div>
</div>''',

    'history': '''<div class="page active" id="history-page">
<div class="home-container">
<div class="history-container">
<h2 class="page-title">📜 Lịch Sử Hoạt Động</h2>
<div class="history-list" id="history-list">
<div class="history-item">
<span class="history-time">Hôm nay</span>
<span class="history-action">Khởi động hệ thống</span>
<span class="history-user">Admin</span>
</div>
</div>
</div>
</div>
</div>''',

    'theme': '''<div class="page active" id="theme-page">
<div class="home-container">
<div class="theme-container">
<h2 class="page-title">🎨 Giao Diện</h2>
<div class="theme-options">
<label>
<input type="radio" name="theme" value="light" checked>
<span>Sáng</span>
</label>
<label>
<input type="radio" name="theme" value="dark">
<span>Tối</span>
</label>
<label>
<input type="radio" name="theme" value="auto">
<span>Tự động</span>
</label>
</div>
</div>
</div>
</div>''',

    'settings': '''<div class="page active" id="settings-page">
<div class="home-container">
<div class="settings-container">
<h2 class="page-title">⚙️ Cài Đặt</h2>
<div class="settings-form">
<div class="setting-item">
<label>Tên Ứng Dụng:</label>
<input type="text" class="input-field" value="Bot Manager">
</div>
<div class="setting-item">
<label>Email Liên Lạc:</label>
<input type="email" class="input-field" placeholder="admin@example.com">
</div>
<button class="btn btn-primary">Lưu Cài Đặt</button>
</div>
</div>
</div>
</div>''',

    'profile': '''<div class="page active" id="profile-page">
<div class="home-container">
<div class="profile-card">
<h2 class="page-title">👤 Hồ Sơ Của Tôi</h2>
<div class="profile-info">
<div class="profile-avatar"></div>
<div class="profile-details">
<p><strong>Tên:</strong> <span id="profile-full-name">User Name</span></p>
<p><strong>Email:</strong> <span id="profile-email">user@example.com</span></p>
<p><strong>Ngày Tham Gia:</strong> <span id="profile-joined">01/01/2024</span></p>
<button class="btn btn-primary" id="edit-profile-btn">Chỉnh Sửa</button>
</div>
</div>
</div>
</div>
</div>''',
}

# Create each page
extra_scripts = {
    'manager': '    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>\n'
}

for page_name, page_content in pages_html.items():
    page_dir = Path(f'web/{page_name}')
    page_file = page_dir / 'index.html'
    
    # Get page title
    titles = {
        'manager': 'Quan Ly Bot - Manager',
        'bots': 'Quan Ly Bot - Bots',
        'create': 'Quan Ly Bot - Create',
        'rental': 'Quan Ly Bot - Rental',
        'payment': 'Quan Ly Bot - Payment',
        'commands': 'Quan Ly Bot - Commands',
        'statistics': 'Quan Ly Bot - Statistics',
        'users': 'Quan Ly Bot - Users',
        'history': 'Quan Ly Bot - History',
        'theme': 'Quan Ly Bot - Theme',
        'settings': 'Quan Ly Bot - Settings',
        'profile': 'Quan Ly Bot - Profile',
    }
    
    # Build HTML
    html_content = f'''<!-- {page_name}/index.html -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titles.get(page_name, 'Quan Ly Bot')}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
{extra_scripts.get(page_name, '')}{home_template[home_template.find('<link rel="stylesheet"'):home_template.find('<link rel="stylesheet"') + home_template[home_template.find('<link rel="stylesheet"'):].find('\n') + 1]}
</head>
<body>
{sidebar}

<section class="home-section">
{page_content}
</section>
{footer}
</body>
</html>
'''
    
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Created: {page_name}")

print("\n✅ All pages created with proper content!")
