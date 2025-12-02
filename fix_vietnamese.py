#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
from pathlib import Path

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True)

# Vietnamese text that should appear in titles
page_titles = {
    'manager': 'Quản Lý Bot - Manager',
    'home': 'Quản Lý Bot - Home',
    'bots': 'Quản Lý Bot - Bots',
    'commands': 'Quản Lý Bot - Commands',
    'create': 'Quản Lý Bot - Create',
    'settings': 'Quản Lý Bot - Settings',
    'profile': 'Quản Lý Bot - Profile',
    'users': 'Quản Lý Bot - Users',
    'payment': 'Quản Lý Bot - Payment',
    'rental': 'Quản Lý Bot - Rental',
    'statistics': 'Quản Lý Bot - Statistics',
    'theme': 'Quản Lý Bot - Theme',
    'history': 'Quản Lý Bot - History',
    'login': 'Quản Lý Bot - Login',
    'register': 'Quản Lý Bot - Register',
    'forgot-password': 'Quản Lý Bot - Forgot Password',
}

fixed_count = 0
for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    # Read as binary first
    try:
        with open(fpath, 'rb') as f:
            raw_bytes = f.read()
    except Exception as e:
        print(f'Error reading {fpath}: {e}')
        continue
    
    # Try to decode with original encoding
    content = None
    original_encoding = None
    for enc in ['cp1252', 'latin-1', 'iso-8859-1', 'utf-8']:
        try:
            content = raw_bytes.decode(enc)
            original_encoding = enc
            break
        except:
            pass
    
    if not content:
        print(f'Could not decode: {fpath}')
        continue
    
    original = content
    
    # Get page type from path
    page_type = None
    for ptype, title in page_titles.items():
        if ptype in fpath:
            page_type = ptype
            break
    
    # Fix title if found
    if page_type and page_titles[page_type] in page_titles.values():
        # Replace any mojibake title with correct one
        content = content.replace(content[content.find('<title>') + 7:content.find('</title>')], page_titles[page_type])
    
    # Fix common Vietnamese text issues
    fixes = {
        'Quận Lý': 'Quản Lý',
        'Qu?n Ly': 'Quản Lý',
        'Quáº£n LÃ½': 'Quản Lý',
        'QuÃ¡n LÃ½': 'Quản Lý',
    }
    
    for mojibake, correct in fixes.items():
        content = content.replace(mojibake, correct)
    
    # Write back as UTF-8
    if content != original:
        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            page_name = Path(fpath).parent.name or 'root'
            print(f'✓ Fixed: {page_name}/index.html')
            fixed_count += 1
        except Exception as e:
            print(f'Error writing {fpath}: {e}')

print(f'\n✓ Tổng cộng đã sửa: {fixed_count} file')
