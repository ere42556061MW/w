#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = sorted(glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True))

def clean_file(fpath):
    """Read file with all encodings, detect mojibake, and write clean UTF-8"""
    try:
        # Read as binary
        with open(fpath, 'rb') as f:
            raw = f.read()
        
        # Remove UTF-8 BOM if present (EF BB BF)
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        
        # Try to decode - if it has mojibake, this will show it
        text = raw.decode('utf-8', errors='replace')
        
        # Fix common mojibake patterns from cp1252→UTF-8 double encoding
        mojibake_map = {
            # Common double-encoding: UTF-8 bytes read as Latin-1
            'Ã¡': 'á',  # a with acute
            'Ã©': 'é',  # e with acute
            'Ã­': 'í',  # i with acute
            'Ã³': 'ó',  # o with acute
            'Ãº': 'ú',  # u with acute
            'Ã ': 'à',  # a with grave
            'Ã¨': 'è',  # e with grave
            'Ã²': 'ò',  # o with grave
            'Ã¹': 'ù',  # u with grave
            'Ã£': 'ã',  # a with tilde
            'Ã±': 'ñ',  # n with tilde
            'Ã´': 'ô',  # o with circumflex
            'Â»': '',   # broken chars
            'Â¡': '',   # broken chars
            'Â¢': '',   # broken chars
            'Â§': '',   # broken chars
            'Â¦': '',   # broken chars
            'Â¬': '',   # broken chars
            'Â­': '',   # broken chars
            'Â¾': '',   # broken chars
            'Â¿': '',   # broken chars
            'Ã‚': '',   # broken chars
            'Ã€': '',   # broken chars
            'Ã„': '',   # broken chars
            'Ã…': '',   # broken chars
            'Ã†': '',   # broken chars
            'Ã‡': '',   # broken chars
            'ÃƒÆ': '',  # broken triple
            'ÃƒÂ': '',  # broken triple
            'Ã¢': '',   # broken chars
            # Specific Vietnamese mojibake fixes
            'cÃƒÆ\'Ã‚Â¡ch': 'chế độ',
            'dÃƒÂ¡Ã‚Â»Ã¢â‚¬Â¦': 'đầy',
            'dÃƒÆ\'Ã‚Â ng': 'đủ',
            'mÃƒÂ¡Ã‚Â»Ã¢â€žÂ¢t': 'mật',
        }
        
        for mojibake, correct in mojibake_map.items():
            text = text.replace(mojibake, correct)
        
        # Write clean UTF-8 (no BOM, proper formatting)
        with open(fpath, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        
        page = os.path.basename(os.path.dirname(fpath)) or 'root'
        return True, page
        
    except Exception as e:
        return False, str(e)

fixed = []
failed = []

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    success, msg = clean_file(fpath)
    if success:
        fixed.append(msg)
        print(f'✓ {msg}')
    else:
        failed.append((fpath, msg))
        print(f'✗ {msg}')

print(f'\n✓ Fixed: {len(fixed)} files')
if failed:
    print(f'✗ Failed: {len(failed)} files')
    for fpath, err in failed:
        print(f'  {fpath}: {err}')
