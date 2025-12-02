#!/usr/bin/env python3
import os
import glob

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True)

# Map of mojibake to correct Vietnamese text
fixes = {
    'QuA¡n LA½': 'Quản Lý',
    'Quáº£n LA½': 'Quản Lý',
    'Quá\xa0n LÃ½': 'Quản Lý',
}

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    # Try reading with different encodings
    content = None
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            with open(fpath, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except:
            continue
    
    if not content:
        print(f'Could not read: {fpath}')
        continue
    
    original = content
    # Fix mojibake in titles
    for mojibake, correct in fixes.items():
        content = content.replace(mojibake, correct)
    
    # Remove stray backtick-n before sidebar-backdrop
    content = content.replace('-->`n', '-->\n')
    content = content.replace('<!-- Sidebar Navigation -->`n', '<!-- Sidebar Navigation -->\n')
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {os.path.basename(fpath)} ({os.path.dirname(fpath).split(os.sep)[-1]})')

print('\nDone! All HTML files have been fixed and encoded as UTF-8.')
