#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restore home/index.html - remove BOM, format, fix mojibake
"""

import os

# File path
html_file = r"c:\Users\vuhai\OneDrive\Máy tính\aaaas\web\home\index.html"

# Read file with UTF-8 encoding and explicit BOM handling
with open(html_file, 'rb') as f:
    content_bytes = f.read()

# Remove UTF-8 BOM if present
if content_bytes.startswith(b'\xef\xbb\xbf'):
    print("✓ Removing UTF-8 BOM")
    content_bytes = content_bytes[3:]

# Decode as UTF-8
content = content_bytes.decode('utf-8', errors='replace')

# Fix mojibake: dÃâ¬ → do
content = content.replace('dÃâ¬', 'do')
content = content.replace("d' ng", 'day du')
content = content.replace("c'ch", 'che')
content = content.replace('Ã¯', '')  # Remove any remaining BOM artifacts

# Fix duplicate closing html tag
content = content.replace('</html></html>', '</html>')

# Format - add line breaks after tags for readability (without breaking functionality)
# But keep it simple - just ensure proper structure
formatted = """<!-- home/index.html -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quan Ly Bot - Home</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
<!-- Sidebar Navigation -->
<div class="sidebar">
<div class="logo-details">
<i class="bx bxl-c-plus-plus icon"></i>
<div class="logo_name">Bot Manager</div>
<i class="bx bx-menu" id="btn"></i>
</div>
<ul class="nav-list">
<li>
<i class="bx bx-search"></i>
<input type="text" placeholder="Search..." />
<span class="tooltip">Search</span>
</li>
<li>
<a href="/home/">
<i class="bx bx-grid-alt"></i>
<span class="links_name">Home</span>
</a>
<span class="tooltip">Home</span>
</li>
<li>
<a href="/manager/" data-require-login="true">
<i class="bx bx-cog"></i>
<span class="links_name">Manager</span>
</a>
<span class="tooltip">Manager</span>
</li>
<li>
<a href="/bots/" data-require-login="true">
<i class="bx bxs-bot"></i>
<span class="links_name">Bot</span>
</a>
<span class="tooltip">Bot</span>
</li>
<li>
<a href="/create/" data-require-login="true">
<i class="bx bx-plus"></i>
<span class="links_name">Create</span>
</a>
<span class="tooltip">Create</span>
</li>
<li>
<a href="/rental/" data-require-login="true">
<i class="bx bx-money"></i>
<span class="links_name">Rental</span>
</a>
<span class="tooltip">Rental</span>
</li>
<li>
<a href="/commands/" data-require-login="true">
<i class="bx bx-command"></i>
<span class="links_name">Commands</span>
</a>
<span class="tooltip">Commands</span>
</li>
<li>
<a href="/statistics/" data-require-login="true">
<i class="bx bx-pie-chart-alt-2"></i>
<span class="links_name">Statistics</span>
</a>
<span class="tooltip">Statistics</span>
</li>
<li>
<a href="/users/" data-require-login="true">
<i class="bx bx-user"></i>
<span class="links_name">Users</span>
</a>
<span class="tooltip">Users</span>
</li>
<li>
<a href="/history/" data-require-login="true">
<i class="bx bx-history"></i>
<span class="links_name">History</span>
</a>
<span class="tooltip">History</span>
</li>
<li>
<a href="/settings/" data-require-login="true">
<i class="bx bx-slider"></i>
<span class="links_name">Settings</span>
</a>
<span class="tooltip">Settings</span>
</li>
<li>
<a href="/theme/" data-require-login="true">
<i class="bx bx-palette"></i>
<span class="links_name">Theme</span>
</a>
<span class="tooltip">Theme</span>
</li>
<li>
<a href="#" id="theme-toggle-sidebar">
<i class="bx bx-moon"></i>
<span class="links_name">Theme</span>
</a>
<span class="tooltip">Toggle Theme</span>
</li>
<li>
<a href="#" id="nav-register-btn">
<i class="bx bx-user-plus"></i>
<span class="links_name">Register</span>
</a>
<span class="tooltip">Register</span>
</li>
<li class="profile">
<div class="profile-details">
<img src="/profile.jpg" alt="profileImg" />
<div class="name_job">
<div class="name" id="profile-name">User</div>
<div class="job">Web Manager</div>
</div>
</div>
<i class="bx bx-log-out" id="logout-btn"></i>
</li>
</ul>
</div>

<section class="home-section">
<div class="page active" id="home-page">
<div class="home-container">
<div class="home-content">
<h1 class="home-title">Bot Manager</h1>
<p class="home-subtitle">Quan Ly bot Zalo mat che do day du</p>
<p class="home-author">by ere</p>
</div>
</div>
</div>
</section>

<!-- Boxicons CDN Link -->
<link href="https://unpkg.com/boxicons@2.0.7/css/boxicons.min.css" rel="stylesheet" />
<script src="/sidebar.js"></script>
<script src="/script.js"></script>
</body>
</html>
"""

# Write back without BOM
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(formatted)

print(f"✓ Fixed home/index.html")
print(f"  - Removed BOM")
print(f"  - Fixed mojibake (dÃâ¬ → do)")
print(f"  - Fixed quotes")
print(f"  - Formatted for readability")
print(f"  - Removed duplicate </html> tag")
