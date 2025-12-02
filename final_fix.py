#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import re

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = sorted(glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True))

fixed_count = 0

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    try:
        # Read as UTF-8
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        original = text
        
        # Remove UTF-8 BOM
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Remove stray mojibake patterns
        text = re.sub(r'Ã¯»¿', '', text)  # UTF-8 BOM as mojibake
        
        # Fix specific substring mojibakes
        replacements = [
            ('cÃ¶th', 'chế độ'),
            ('dÃ ÂºnÃ§', 'đầy đủ'),
            ('m»\x9dt', 'mật'),
        ]
        
        for pattern, replacement in replacements:
            if pattern in text:
                text = text.replace(pattern, replacement)
        
        # Clean up broken characters that don't belong
        text = re.sub(r'[Â°±²³´µ¶·¸¹º»¼½¾¿]', '', text)
        text = re.sub(r'[€‚ƒ„…†‡ˆ‰Š‹ŒŽ''""•–—˜™š›œžŸ]', '', text)
        
        if text != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(text)
            page = os.path.basename(os.path.dirname(fpath)) or 'root'
            print(f'✓ {page}')
            fixed_count += 1
    
    except Exception as e:
        print(f'✗ {fpath}: {e}')

print(f'\n✓ Fixed {fixed_count} files')
