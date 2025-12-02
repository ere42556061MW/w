#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import codecs

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True)

def fix_mojibake_utf8(text):
    """Converts UTF-8 mojibake back to proper text"""
    # UTF-8 double-encoded as Latin-1 appears as: Ã followed by accented char
    # e.g., "mÃ¡" is "m" + UTF-8 byte 0xC3 + UTF-8 byte 0xA1 = Vietnamese "á"
    
    # Try to detect and fix
    try:
        # Encode to latin-1 bytes, then decode as UTF-8
        return text.encode('latin-1').decode('utf-8')
    except:
        return text

fixed_count = 0

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    try:
        # Read as-is (UTF-8 with mojibake)
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        original = text
        
        # Remove BOM
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Try to fix mojibake
        fixed_text = fix_mojibake_utf8(text)
        
        # If different, use fixed version
        if fixed_text != text:
            text = fixed_text
        
        # Write back
        with open(fpath, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        
        if text != original:
            page = os.path.basename(os.path.dirname(fpath)) or 'root'
            print(f'✓ Fixed mojibake: {page}')
            fixed_count += 1
            
    except Exception as e:
        print(f'⚠ {fpath}: {e}')

print(f'\n✓ Xong: {fixed_count} file')
