# -*- coding: utf-8 -*-
"""
Fix all HTML pages with proper encoding and structure.
Based on the fixed home/index.html template.
"""

import os
from pathlib import Path

# Template pages with their specific content
pages_content = {
    'login': {
        'title': 'Quan Ly Bot - Login',
        'page_id': 'login-page',
        'page_class': '',
        'content': '''<div class="page active" id="login-page">
<div class="home-container">
<div class="create-card" style="max-width: 450px;">
<h2 class="create-title">Đăng Nhập</h2>
<p style="text-align: center; color: #6b7280; margin-bottom: 30px;">Chào mừng trở lại!</p>
<div class="action-group">
<label>Email hoặc Username:</label>
<input type="text" class="input-field" id="login-username" placeholder="Nhập email hoặc username...">
</div>
<div class="action-group">
<label>Mật khẩu:</label>
<input type="password" class="input-field" id="login-password" placeholder="Nhập mật khẩu...">
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin: 0;">
<input type="checkbox" id="remember-me" style="cursor: pointer;">
<span style="font-size: 14px; color: #6b7280;">Ghi nhớ đăng nhập</span>
</label>
<a href="#" id="forgot-password" style="font-size: 14px; color: #667eea; text-decoration: none;">Quên mật khẩu?</a>
</div>
<button class="btn btn-primary" id="login-btn">Đăng Nhập</button>
<div style="text-align: center; margin: 20px 0; color: #9ca3af;">
<span>hoặc</span>
</div>
<div style="display: flex; gap: 10px; margin-bottom: 20px;">
<button class="btn" id="login-google" style="flex: 1; background: #ea4335; color: white; margin: 0;">
Đăng Google
</button>
<button class="btn" id="login-facebook" style="flex: 1; background: #1877f2; color: white; margin: 0;">
Đăng Facebook
</button>
</div>
<div style="text-align: center; font-size: 14px; color: #6b7280;">
Chưa có tài khoản? <a href="#" id="goto-register" style="color: #667eea; text-decoration: none; font-weight: 600;">Đăng ký ngay</a>
</div>
</div>
</div>
</div>'''
    },
    'register': {
        'title': 'Quan Ly Bot - Register',
        'page_id': 'register-page',
        'page_class': '',
        'content': '''<div class="page active" id="register-page">
<div class="home-container">
<div class="create-card" style="max-width: 450px;">
<h2 class="create-title">Đăng Ký</h2>
<p style="text-align: center; color: #6b7280; margin-bottom: 30px;">Tạo tài khoản mới miễn phí</p>
<div class="action-group">
<label>Họ và tên:</label>
<input type="text" class="input-field" id="register-fullname" placeholder="Nguyễn Văn A">
</div>
<div class="action-group">
<label>Email:</label>
<input type="email" class="input-field" id="register-email" placeholder="example@email.com">
</div>
<div class="action-group">
<label>Username:</label>
<input type="text" class="input-field" id="register-username" placeholder="username123">
</div>
<div class="action-group">
<label>Mật khẩu:</label>
<input type="password" class="input-field" id="register-password" placeholder="Tối thiểu 8 ký tự">
</div>
<div class="action-group">
<label>Xác nhận mật khẩu:</label>
<input type="password" class="input-field" id="register-confirm" placeholder="Nhập lại mật khẩu">
</div>
<label style="display: flex; align-items: center; gap: 8px; cursor: pointer; margin-bottom: 20px;">
<input type="checkbox" id="accept-terms" style="cursor: pointer;">
<span style="font-size: 14px; color: #6b7280;">Tôi đồng ý với <a href="#" style="color: #667eea;">Điều khoản dịch vụ</a></span>
</label>
<button class="btn btn-primary" id="register-btn">Tạo Tài Khoản</button>
<div style="text-align: center; margin: 20px 0; color: #9ca3af;">
<span>hoặc</span>
</div>
<div style="display: flex; gap: 10px; margin-bottom: 20px;">
<button class="btn" id="register-google" style="flex: 1; background: #ea4335; color: white; margin: 0;">
Đăng Google
</button>
<button class="btn" id="register-facebook" style="flex: 1; background: #1877f2; color: white; margin: 0;">
Đăng Facebook
</button>
</div>
<div style="text-align: center; font-size: 14px; color: #6b7280;">
Đã có tài khoản? <a href="#" id="goto-login" style="color: #667eea; text-decoration: none; font-weight: 600;">Đăng nhập</a>
</div>
</div>
</div>
</div>'''
    },
    'forgot-password': {
        'title': 'Quan Ly Bot - Forgot Password',
        'page_id': 'forgot-page',
        'page_class': '',
        'content': '''<div class="page active" id="forgot-page">
<div class="home-container">
<div class="create-card" style="max-width: 450px;">
<h2 class="create-title">Quên Mật Khẩu</h2>
<p style="text-align: center; color: #6b7280; margin-bottom: 30px;">Nhập email để đặt lại mật khẩu</p>
<div class="action-group">
<label>Email đã đăng ký:</label>
<input type="email" class="input-field" id="forgot-email" placeholder="example@email.com">
</div>
<button class="btn btn-primary" id="reset-password-btn">Gửi Link Đặt Lại</button>
<div style="text-align: center; font-size: 14px; color: #6b7280; margin-top: 20px;">
<a href="#" id="back-to-login" style="color: #667eea; text-decoration: none; font-weight: 600;">Quay lại đăng nhập</a>
</div>
</div>
</div>
</div>'''
    },
}

# Read the home/index.html template
home_path = Path('web/home/index.html')
with open(home_path, 'r', encoding='utf-8') as f:
    home_content = f.read()

# Extract header and footer from home page
import re

# Find the opening body tag and closing body tag
header_match = re.search(r'(.*?)<section class="home-section">', home_content, re.DOTALL)
footer_match = re.search(r'</section>(.*)', home_content, re.DOTALL)

if header_match and footer_match:
    header = header_match.group(1)
    footer = footer_match.group(1)
    
    # Create pages
    for page_name, page_data in pages_content.items():
        page_dir = Path(f'web/{page_name}')
        page_dir.mkdir(exist_ok=True)
        
        page_html = f'''<!-- {page_name}/index.html -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data['title']}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
{header.strip()}
<section class="home-section">
{page_data['content']}
</section>
{footer.strip()}
</body>
</html>'''
        
        page_file = page_dir / 'index.html'
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_html)
        print(f"✓ Created: {page_file}")

print("\nAll pages fixed successfully!")
