# split_pages.py
# -*- coding: utf-8 -*-
import re
import os
from pathlib import Path

# Read the original HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract navigation HTML
nav_match = re.search(r'(<!-- Navigation -->.*?</nav>)', content, re.DOTALL)
navigation = nav_match.group(1) if nav_match else ''

# Page mapping: id attribute -> directory name
page_mapping = {
    'login-page': 'login',
    'register-page': 'register',
    'forgot-page': 'forgot-password',
    'home-page': 'home',
    'manager-page': 'manager',
    'bots-page': 'bots',
    'create-page': 'create',
    'rental-page': 'rental',
    'payment-page': 'payment',
    'commands-page': 'commands',
    'statistics-page': 'statistics',
    'users-page': 'users',
    'history-page': 'history',
    'theme-page': 'theme',
    'settings-page': 'settings',
    'profile-page': 'profile',
}

# Function to extract page content by finding matching closing div
def extract_page_content(content, page_id):
    # Find the opening div
    pattern = rf'<div class="page[^"]*" id="{re.escape(page_id)}">'
    match = re.search(pattern, content)
    if not match:
        return None
    
    start_pos = match.start()
    
    # Find the matching closing div by counting divs
    pos = match.end()
    div_count = 1
    depth = 0
    
    while pos < len(content) and div_count > 0:
        # Find next <div or </div>
        next_div = re.search(r'</?div', content[pos:])
        if not next_div:
            break
        
        next_pos = pos + next_div.start()
        tag = content[next_pos:next_pos + next_div.end()]
        
        if tag.startswith('</div'):
            div_count -= 1
            if div_count == 0:
                # Found the closing tag for our page div
                end_pos = next_pos + len('</div>')
                return content[start_pos:end_pos]
        elif tag.startswith('<div'):
            # Check if it's a self-closing div (unlikely but possible)
            if not re.search(r'/>', content[next_pos:next_pos + 50]):
                div_count += 1
        
        pos = next_pos + 1
    
    return None

# Extract page sections
pages = {}
for page_id, page_dir in page_mapping.items():
    page_content = extract_page_content(content, page_id)
    if page_content:
        pages[page_dir] = page_content
    else:
        print(f"Warning: Could not find {page_id}")

# Update navigation to use href links
def update_nav_links(nav_html, current_page):
    # Convert nav-link buttons with data-page to <a> tags
    def replace_nav_link(match):
        extra_classes = match.group(1) or ''
        data_page = match.group(2)
        attrs = match.group(3) or ''
        text = match.group(4)
        
        # Map page names
        page_map = {
            'home': 'home',
            'manager': 'manager',
            'bots': 'bots',
            'create': 'create',
            'rental': 'rental',
            'commands': 'commands',
            'statistics': 'statistics',
            'users': 'users',
            'history': 'history',
            'theme': 'theme',
            'settings': 'settings',
        }
        
        href_page = page_map.get(data_page, data_page)
        href = f'/{href_page}/'
        
        # Build class attribute
        # Remove 'active' from extra_classes first, then add if needed
        extra_classes_clean = extra_classes.replace(' active', '').replace('active', '').strip()
        classes = 'nav-link'
        if extra_classes_clean:
            classes += ' ' + extra_classes_clean
        # Add active class only if current page
        if href_page == current_page:
            classes += ' active'
        
        return f'<a class="{classes}" href="{href}"{attrs}>{text}</a>'
    
    # Replace button nav-links (only those with data-page)
    nav_html = re.sub(
        r'<button class="nav-link([^"]*)" data-page="(\w+)"([^>]*)>(.*?)</button>',
        replace_nav_link,
        nav_html
    )
    
    # Convert nav-dropdown-item divs to <a> tags
    def replace_dropdown_item(match):
        data_page = match.group(1)
        other_attrs = match.group(2) or ''
        text = match.group(3)
        
        # Map page names
        page_map = {
            'home': 'home',
            'manager': 'manager',
            'bots': 'bots',
            'create': 'create',
            'rental': 'rental',
            'commands': 'commands',
            'statistics': 'statistics',
            'users': 'users',
            'history': 'history',
            'theme': 'theme',
            'settings': 'settings',
        }
        
        href_page = page_map.get(data_page, data_page)
        href = f'/{href_page}/'
        
        # Add active class if current page
        active_class = ' active' if href_page == current_page else ''
        
        return f'<a class="nav-dropdown-item{active_class}" href="{href}"{other_attrs}>{text}</a>'
    
    # Replace dropdown items - capture data-page and any other attributes
    nav_html = re.sub(
        r'<div class="nav-dropdown-item" data-page="(\w+)"([^>]*)>(.*?)</div>',
        replace_dropdown_item,
        nav_html
    )
    
    # Update forgot password link in login page
    nav_html = re.sub(
        r'href="#" id="forgot-password"',
        'href="/forgot-password/" id="forgot-password"',
        nav_html
    )
    
    # Update back to login link
    nav_html = re.sub(
        r'href="#" id="back-to-login"',
        'href="/login/" id="back-to-login"',
        nav_html
    )
    
    return nav_html

# Create directories and HTML files
for page_dir, page_content in pages.items():
    # Create directory
    page_path = Path(page_dir)
    page_path.mkdir(exist_ok=True)
    
    # Update navigation for this page
    nav_for_page = update_nav_links(navigation, page_dir)
    
    # Add 'active' class to the page div so it displays
    # Find the page div and add 'active' class if not present
    if 'class="page' in page_content:
        # Replace class="page with class="page active
        page_content = re.sub(
            r'class="page([^"]*)"',
            lambda m: f'class="page{m.group(1)} active"' if 'active' not in m.group(1) else f'class="page{m.group(1)}"',
            page_content,
            count=1  # Only replace the first occurrence (the page div)
        )
    
    # Create HTML file
    html_content = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản Lý Bot - {page_dir.replace("-", " ").title()}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    {nav_for_page}
    
    {page_content}
    
    <script src="/script.js"></script>
</body>
</html>'''
    
    # Write file
    with open(page_path / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created {page_dir}/index.html")

print("Done!")
