# -*- coding: utf-8 -*-
"""
Extract content from existing HTML files and re-encode them properly with UTF-8.
This will fix all the mojibake encoding issues.
"""

import os
import re
from pathlib import Path

# Read the home/index.html as the template
home_path = Path('web/home/index.html')
with open(home_path, 'r', encoding='utf-8') as f:
    home_content = f.read()

# Extract header (before <section class="home-section">)
header_match = re.search(r'(^.*?)<section class="home-section">', home_content, re.DOTALL)
header = header_match.group(1) if header_match else ""

# Extract footer (after closing </section>)
footer_match = re.search(r'</section>(.*?$)', home_content, re.DOTALL)
footer = footer_match.group(1) if footer_match else ""

print("Template extracted")
print(f"Header length: {len(header)}")
print(f"Footer length: {len(footer)}")

# List of pages to fix
pages_to_fix = {
    'manager': {
        'title': 'Quan Ly Bot - Manager',
        'has_socket': True,
        'page_id': 'manager-page'
    },
    'bots': {
        'title': 'Quan Ly Bot - Bots',
        'page_id': 'bots-page'
    },
    'create': {
        'title': 'Quan Ly Bot - Create',
        'page_id': 'create-page'
    },
    'rental': {
        'title': 'Quan Ly Bot - Rental',
        'page_id': 'rental-page'
    },
    'payment': {
        'title': 'Quan Ly Bot - Payment',
        'page_id': 'payment-page'
    },
    'commands': {
        'title': 'Quan Ly Bot - Commands',
        'page_id': 'commands-page'
    },
    'statistics': {
        'title': 'Quan Ly Bot - Statistics',
        'page_id': 'statistics-page'
    },
    'users': {
        'title': 'Quan Ly Bot - Users',
        'page_id': 'users-page'
    },
    'history': {
        'title': 'Quan Ly Bot - History',
        'page_id': 'history-page'
    },
    'theme': {
        'title': 'Quan Ly Bot - Theme',
        'page_id': 'theme-page'
    },
    'settings': {
        'title': 'Quan Ly Bot - Settings',
        'page_id': 'settings-page'
    },
    'profile': {
        'title': 'Quan Ly Bot - Profile',
        'page_id': 'profile-page'
    },
}

# Try to read and extract content from existing garbled files
def extract_content_from_file(filepath):
    """Try to extract page content from a garbled file"""
    try:
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
        
        # Try different encodings
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                content = raw_bytes.decode(encoding)
                return content
            except:
                continue
        return None
    except:
        return None

# For pages with existing content
pages_with_content = {}

for page_name in pages_to_fix.keys():
    page_file = Path(f'web/{page_name}/index.html')
    if page_file.exists():
        content = extract_content_from_file(page_file)
        if content:
            pages_with_content[page_name] = content
            print(f"✓ Extracted content from {page_name}")
        else:
            print(f"✗ Could not extract content from {page_name}")

# Now create properly encoded files
extra_scripts = {
    'manager': '''    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
'''
}

for page_name, page_info in pages_to_fix.items():
    page_dir = Path(f'web/{page_name}')
    page_dir.mkdir(exist_ok=True)
    
    # Start building the HTML
    html_lines = [
        f'<!-- {page_name}/index.html -->',
        '<!DOCTYPE html>',
        '<html lang="vi">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'    <title>{page_info["title"]}</title>',
        '    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>',
    ]
    
    # Add extra scripts if needed
    if page_info.get('has_socket'):
        html_lines.append('    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>')
    
    html_lines.append('    <link rel="stylesheet" href="/styles.css">')
    html_lines.append('</head>')
    html_lines.append('<body>')
    
    # Add sidebar from template
    # Extract sidebar from header
    sidebar_match = re.search(r'<!-- Sidebar Navigation -->.*?</div>\s*<section', header, re.DOTALL)
    if sidebar_match:
        sidebar_content = sidebar_match.group(0).replace('<section', '')
        html_lines.append(sidebar_content.strip())
    
    # Add page content
    html_lines.append('<section class="home-section">')
    
    # Try to extract existing page content
    if page_name in pages_with_content:
        existing = pages_with_content[page_name]
        page_match = re.search(rf'<div class="page[^"]*" id="{page_info["page_id"]}".*?</div>\s*</section>', existing, re.DOTALL)
        if page_match:
            content = page_match.group(0).replace('</section>', '')
            html_lines.append(content.strip())
        else:
            # Fallback: create empty page
            html_lines.append(f'<div class="page" id="{page_info["page_id"]}">')
            html_lines.append(f'<div class="home-container">')
            html_lines.append(f'<p>Content for {page_name}</p>')
            html_lines.append('</div>')
            html_lines.append('</div>')
    else:
        # Create empty page structure
        html_lines.append(f'<div class="page" id="{page_info["page_id"]}">')
        html_lines.append(f'<div class="home-container">')
        html_lines.append(f'<p>Content for {page_name}</p>')
        html_lines.append('</div>')
        html_lines.append('</div>')
    
    html_lines.append('</section>')
    
    # Add footer
    # Extract footer scripts
    footer_lines = footer.strip().split('\n')
    for line in footer_lines:
        html_lines.append(line)
    
    html_lines.append('</body>')
    html_lines.append('</html>')
    
    # Write file
    page_file = page_dir / 'index.html'
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    
    print(f"✓ Created: {page_file}")

print("\nAll pages have been processed!")
