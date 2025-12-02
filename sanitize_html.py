#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import re

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True)

# Map mojibake patterns to correct Vietnamese
fixes = {
    'Quáº£n LÃ½': 'Quản Lý',
    'QuÃ¡n LÃ½': 'Quản Lý',
    'Quán Lý': 'Quản Lý',
    'Quà n Lý': 'Quản Lý',
}

fixed_count = 0

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    try:
        # Read as UTF-8 (which will show mojibake)
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        original = text
        
        # Remove UTF-8 BOM if present
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Remove extra line breaks added during encoding
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'>\s+<', '><', text)
        
        # Fix mojibake Vietnamese text
        for mojibake, correct in fixes.items():
            text = text.replace(mojibake, correct)
        
        # Write back clean UTF-8 (no BOM)
        with open(fpath, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        
        if text != original:
            page = os.path.basename(os.path.dirname(fpath)) or 'root'
            print(f'✓ Cleaned: {page}')
            fixed_count += 1
            
    except Exception as e:
        print(f'ERROR {fpath}: {e}')

print(f'\n✓ Tổng số file được làm sạch: {fixed_count}')
