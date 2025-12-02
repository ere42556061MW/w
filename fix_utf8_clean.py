#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True)

fixed = []

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    # Read raw bytes and decode with original encoding (likely cp1252/windows-1252)
    try:
        with open(fpath, 'rb') as f:
            raw = f.read()
        
        # Try to decode from original encoding
        text = None
        for encoding in ['cp1252', 'latin-1', 'iso-8859-1']:
            try:
                text = raw.decode(encoding)
                break
            except:
                pass
        
        if not text:
            text = raw.decode('utf-8', errors='replace')
        
        # Clean up encoding artifacts - remove UTF-8 BOM if present
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Write back as pure UTF-8
        with open(fpath, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        
        page = os.path.basename(os.path.dirname(fpath)) or 'root'
        fixed.append(page)
        
    except Exception as e:
        print(f'ERROR {fpath}: {e}')

print(f'✓ Đã re-encode {len(fixed)} file sang UTF-8')
for p in sorted(fixed):
    print(f'  - {p}')
