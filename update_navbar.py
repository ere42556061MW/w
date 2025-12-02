#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Sidebar HTML replacement
sidebar_html = """    <!-- Sidebar Navigation -->
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
                <a href="#" id="nav-login-btn">
                    <i class="bx bx-log-in"></i>
                    <span class="links_name">Login</span>
                </a>
                <span class="tooltip">Login</span>
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
    <section class="home-section">"""

def update_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace navbar with sidebar
    content = re.sub(
        r'    <!-- Navigation -->[\s\S]*?</nav>\s*',
        sidebar_html + '\n    ',
        content
    )
    
    # Replace closing div with closing section
    content = re.sub(
        r'    </div>\s*\n    <script src="/script.js"></script>',
        '    </div>\n    </section>\n    \n    <!-- Boxicons CDN Link -->\n    <link href="https://unpkg.com/boxicons@2.0.7/css/boxicons.min.css" rel="stylesheet" />\n    <script src="/script.js"></script>\n    <script src="/sidebar.js"></script>',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {filepath}")

# Find and update all index.html files in web subfolders
web_dir = Path('web')
subdirs = [d for d in web_dir.iterdir() if d.is_dir() and (d / 'index.html').exists()]
subdirs = [d for d in subdirs if d.name not in ['__pycache__']]

for subdir in subdirs:
    index_file = subdir / 'index.html'
    if index_file.exists():
        try:
            update_html_file(str(index_file))
        except Exception as e:
            print(f"Error updating {index_file}: {e}")

print(f"\nUpdated {len(subdirs)} HTML files")
