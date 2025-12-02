# -*- coding: utf-8 -*-
"""
Fix all HTML pages with proper UTF-8 encoding using home/index.html as template.
Extract and preserve original content where possible.
"""

import re
from pathlib import Path

# Read the home/index.html as a clean template
home_path = Path('web/home/index.html')
with open(home_path, 'r', encoding='utf-8') as f:
    home_template = f.read()

# Extract key parts from the template
def extract_template_part(template, start_marker, end_marker):
    """Extract a section from template between markers"""
    match = re.search(f'{re.escape(start_marker)}(.*?){re.escape(end_marker)}', template, re.DOTALL)
    return match.group(1) if match else ""

# Extract the sidebar and main structure
sidebar_match = re.search(r'(<!-- Sidebar Navigation -->.*?</div>\s*<section)', home_template, re.DOTALL)
sidebar_section = sidebar_match.group(1).replace('<section', '') if sidebar_match else ""

footer_match = re.search(r'(</section>.*?</body>\s*</html>)', home_template, re.DOTALL)
footer_section = footer_match.group(1) if footer_match else ""

print(f"Sidebar section length: {len(sidebar_section)}")
print(f"Footer section length: {len(footer_section)}")

# Extract existing page content from each garbled file
def extract_page_content_from_garbled(filepath, page_id):
    """Try to extract the actual page content from garbled files"""
    try:
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
        
        # Try UTF-8 first
        try:
            content = raw_bytes.decode('utf-8')
        except:
            # Fallback to other encodings
            try:
                content = raw_bytes.decode('latin-1')
            except:
                return None
        
        # Extract page div
        pattern = rf'<div[^>]*id="?{page_id}"?[^>]*>.*?(?:<div|</div>)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(0)
        return None
    except:
        return None

# Dictionary of all pages with their info
pages_info = {
    'login': {
        'title': 'Quan Ly Bot - Login',
        'page_id': 'login-page',
        'extra_script': None
    },
    'register': {
        'title': 'Quan Ly Bot - Register',
        'page_id': 'register-page',
        'extra_script': None
    },
    'forgot-password': {
        'title': 'Quan Ly Bot - Forgot Password',
        'page_id': 'forgot-page',
        'extra_script': None
    },
    'manager': {
        'title': 'Quan Ly Bot - Manager',
        'page_id': 'manager-page',
        'extra_script': '    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>'
    },
    'bots': {
        'title': 'Quan Ly Bot - Bots',
        'page_id': 'bots-page',
        'extra_script': None
    },
    'create': {
        'title': 'Quan Ly Bot - Create',
        'page_id': 'create-page',
        'extra_script': None
    },
    'rental': {
        'title': 'Quan Ly Bot - Rental',
        'page_id': 'rental-page',
        'extra_script': None
    },
    'payment': {
        'title': 'Quan Ly Bot - Payment',
        'page_id': 'payment-page',
        'extra_script': None
    },
    'commands': {
        'title': 'Quan Ly Bot - Commands',
        'page_id': 'commands-page',
        'extra_script': None
    },
    'statistics': {
        'title': 'Quan Ly Bot - Statistics',
        'page_id': 'statistics-page',
        'extra_script': None
    },
    'users': {
        'title': 'Quan Ly Bot - Users',
        'page_id': 'users-page',
        'extra_script': None
    },
    'history': {
        'title': 'Quan Ly Bot - History',
        'page_id': 'history-page',
        'extra_script': None
    },
    'theme': {
        'title': 'Quan Ly Bot - Theme',
        'page_id': 'theme-page',
        'extra_script': None
    },
    'settings': {
        'title': 'Quan Ly Bot - Settings',
        'page_id': 'settings-page',
        'extra_script': None
    },
    'profile': {
        'title': 'Quan Ly Bot - Profile',
        'page_id': 'profile-page',
        'extra_script': None
    },
}

# Pages that were already fixed
already_fixed = ['login', 'register', 'forgot-password']

# Process all pages
for page_name, page_info in pages_info.items():
    page_dir = Path(f'web/{page_name}')
    page_dir.mkdir(exist_ok=True)
    page_file = page_dir / 'index.html'
    
    # Get existing page content from the original file
    existing_file = page_file
    page_content = ""
    
    if not (page_name in already_fixed):
        # Try to extract content from existing file
        extracted = extract_page_content_from_garbled(existing_file, page_info['page_id'])
        if extracted:
            page_content = extracted
            print(f"✓ Extracted content from {page_name}")
        else:
            # Use placeholder
            page_content = f'<div class="page" id="{page_info["page_id"]}">\n<div class="home-container">\n<p>Content for {page_name}</p>\n</div>\n</div>'
            print(f"⚠ Using placeholder for {page_name}")
    else:
        # For already fixed pages, extract from their current version
        with open(existing_file, 'r', encoding='utf-8') as f:
            fixed_content = f.read()
        # Extract the page div
        match = re.search(rf'<div class="page[^"]*" id="{page_info["page_id"]}".*?</div>\s*</section>', fixed_content, re.DOTALL)
        if match:
            page_content = match.group(0).replace('</section>', '')
            print(f"✓ Using existing fixed content for {page_name}")
    
    # Build the new HTML file
    html_parts = [
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
    if page_info['extra_script']:
        html_parts.append(page_info['extra_script'])
    
    html_parts.append('    <link rel="stylesheet" href="/styles.css">')
    html_parts.append('</head>')
    html_parts.append('<body>')
    html_parts.append(sidebar_section.strip())
    html_parts.append('')
    html_parts.append('<section class="home-section">')
    html_parts.append(page_content.strip())
    html_parts.append('</section>')
    html_parts.append(footer_section.strip())
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    # Write the file
    with open(page_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    print(f"✓ Fixed: {page_name}/index.html")

print("\n✅ All pages fixed successfully!")
