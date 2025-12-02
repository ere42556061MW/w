#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import chardet

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = sorted(glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True))

def fix_html_file(fpath):
    """Detect actual encoding and convert properly to UTF-8"""
    try:
        with open(fpath, 'rb') as f:
            raw = f.read()
        
        # Detect encoding
        detected = chardet.detect(raw)
        detected_enc = detected.get('encoding', 'utf-8')
        
        # Try detected encoding first
        try:
            text = raw.decode(detected_enc)
        except:
            # Fallback to cp1252 (Windows)
            text = raw.decode('cp1252', errors='replace')
        
        original = text
        
        # Remove BOM
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Remove extra newlines/minification formatting
        if '><' in text and '\n' not in text[:100]:
            # File is minified, that's ok but fix any mojibake
            pass
        
        # Aggressive mojibake fixing
        # These are UTF-8 bytes incorrectly read as Latin-1
        fixes = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã ': 'à', 'Ã¨': 'è', 'Ã²': 'ò', 'Ã¹': 'ù', 'Ã£': 'ã',
            'Ã±': 'ñ', 'Ã´': 'ô', 'Ã¶': 'ö', 'Ã¼': 'ü',
            'Ã'': 'Á', 'ÃŠ': 'É', 'Ã­': 'Í', 'Ã"': 'Ó', 'Ã™': 'Ú',
            'Ã‚': '', 'Ã„': '', 'Ã…': '', 'Ã†': '', 'Ã‡': '', 'Ãˆ': '', 'Ã‰': '', 'ÃŠ': '', 'Ã‹': '', 'ÃŒ': '', 'Ã': '', 'ÃŽ': '', 'Ã': '', 'Ã': '', 'Ã"': '', 'Ã"': '', 'Ã•': '', 'Ã–': '', 'Ã—': '', 'Ã˜': '', 'Ã™': '', 'Ãš': '', 'Ã›': '', 'Ãœ': '', 'Ã': '', 'Ãž': '', 'Ã ': '', 'Â»': '', 'Â¡': '', 'Â¢': '', 'Â£': '', 'Â¤': '', 'Â¥': '', 'Â¦': '', 'Â§': '', 'Â¨': '', 'Â©': '', 'Âª': '', 'Â«': '', 'Â¬': '', 'Â­': '', 'Â®': '', 'Â¯': '', 'Â°': '', 'Â±': '', 'Â²': '', 'Â³': '', 'Â´': '', 'Âµ': '', 'Â¶': '', 'Â·': '', 'Â¸': '', 'Â¹': '', 'Âº': '', 'Â»': '', 'Â¼': '', 'Â½': '', 'Â¾': '', 'Â¿': '', 'ÃƒÆ': '', 'ÃƒÂ': '', 'Ã¢': '', 'â€': '', 'â„': '', 'â‚': '', 'â‚¬': '',
        }
        
        for mojibake, correct in fixes.items():
            text = text.replace(mojibake, correct)
        
        if text != original:
            with open(fpath, 'w', encoding='utf-8', newline='') as f:
                f.write(text)
            page = os.path.basename(os.path.dirname(fpath)) or 'root'
            return True, page
        return False, 'no change'
        
    except Exception as e:
        return False, str(e)

fixed = []

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    success, msg = fix_html_file(fpath)
    if success:
        fixed.append(msg)
        print(f'✓ {msg}')

print(f'\n✓ Total fixed: {len(fixed)}')
