# -*- coding: utf-8 -*-
"""
Extract original page content from garbled files and restore them properly.
"""

import re
from pathlib import Path

# Dictionary mapping page names to their actual content patterns
pages_data = {}

# Read all garbled files and extract their actual content
garbled_files = {
    'manager': 'web/manager/index.html',
    'bots': 'web/bots/index.html',
    'create': 'web/create/index.html',
    'rental': 'web/rental/index.html',
    'payment': 'web/payment/index.html',
    'commands': 'web/commands/index.html',
    'statistics': 'web/statistics/index.html',
    'users': 'web/users/index.html',
    'history': 'web/history/index.html',
    'theme': 'web/theme/index.html',
    'settings': 'web/settings/index.html',
    'profile': 'web/profile/index.html',
}

# First, let's read the current backup files if they exist
import os
backup_dir = Path('.')

# Try to read garbled content
for page_name, file_path in garbled_files.items():
    file_p = Path(file_path)
    if file_p.exists():
        try:
            # Read as binary and try different decodings
            with open(file_p, 'rb') as f:
                raw_bytes = f.read()
            
            # Try UTF-8
            try:
                content = raw_bytes.decode('utf-8')
            except:
                try:
                    content = raw_bytes.decode('latin-1')
                except:
                    content = None
            
            if content:
                # Extract the section between <section class="home-section"> and </section>
                section_match = re.search(r'<section[^>]*>(.+?)</section>', content, re.DOTALL | re.IGNORECASE)
                if section_match:
                    page_content = section_match.group(1).strip()
                    pages_data[page_name] = page_content
                    print(f"✓ Extracted content from {page_name} ({len(page_content)} chars)")
                else:
                    print(f"✗ Could not extract section from {page_name}")
        except Exception as e:
            print(f"✗ Error reading {page_name}: {e}")

# Now update pages with their original content
home_path = Path('web/home/index.html')
with open(home_path, 'r', encoding='utf-8') as f:
    home_template = f.read()

# Extract header and footer from home
sidebar_match = re.search(r'(<!-- Sidebar Navigation -->.*?<section)', home_template, re.DOTALL)
sidebar = sidebar_match.group(1).replace('<section', '') if sidebar_match else ""

footer_match = re.search(r'</section>(.*)', home_template, re.DOTALL)
footer = footer_match.group(1) if footer_match else ""

print("\n" + "="*50)
print("Updating pages with extracted content...")
print("="*50 + "\n")

# Update each page with its extracted content
for page_name, page_content in pages_data.items():
    page_dir = Path(f'web/{page_name}')
    page_file = page_dir / 'index.html'
    
    # Determine page info
    page_configs = {
        'manager': {'title': 'Quan Ly Bot - Manager', 'extra_script': '    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>'},
        'bots': {'title': 'Quan Ly Bot - Bots', 'extra_script': None},
        'create': {'title': 'Quan Ly Bot - Create', 'extra_script': None},
        'rental': {'title': 'Quan Ly Bot - Rental', 'extra_script': None},
        'payment': {'title': 'Quan Ly Bot - Payment', 'extra_script': None},
        'commands': {'title': 'Quan Ly Bot - Commands', 'extra_script': None},
        'statistics': {'title': 'Quan Ly Bot - Statistics', 'extra_script': None},
        'users': {'title': 'Quan Ly Bot - Users', 'extra_script': None},
        'history': {'title': 'Quan Ly Bot - History', 'extra_script': None},
        'theme': {'title': 'Quan Ly Bot - Theme', 'extra_script': None},
        'settings': {'title': 'Quan Ly Bot - Settings', 'extra_script': None},
        'profile': {'title': 'Quan Ly Bot - Profile', 'extra_script': None},
    }
    
    config = page_configs.get(page_name, {})
    
    # Build HTML
    html_parts = [
        f'<!-- {page_name}/index.html -->',
        '<!DOCTYPE html>',
        '<html lang="vi">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <title>{config.get("title", "Quan Ly Bot")}</title>',
        '    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>',
    ]
    
    if config.get('extra_script'):
        html_parts.append(config['extra_script'])
    
    html_parts.extend([
        '    <link rel="stylesheet" href="/styles.css">',
        '</head>',
        '<body>',
        sidebar.strip(),
        '',
        '<section class="home-section">',
        page_content,
        '</section>',
        footer.strip(),
        '</body>',
        '</html>'
    ])
    
    # Write file
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    print(f"✓ Updated: {page_name}")

print("\n✅ All pages have been updated with original content!")
