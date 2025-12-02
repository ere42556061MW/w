#!/usr/bin/env python3
# -*- coding: utf-8 -*-

home_file = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web\home\index.html'

with open(home_file, 'rb') as f:
    raw = f.read()

# Decode as UTF-8 (will show mojibake)
text = raw.decode('utf-8', errors='replace')

# The mojibake subtitle - replace with clean Vietnamese
# Original intent seems to be: "Quản Lý bot Zalo mật chế độ đầy đủ" (Manage Zalo bots with full features)
text = text.replace('mÃƒÂ¡Ã‚Â»Ã¢â€žÂ¢t', 'mật')
text = text.replace('cÃƒÆ\'Ã‚Â¡ch', 'chế độ')  
text = text.replace('dÃƒÂ¡Ã‚Â»Ã¢â‚¬Â¦ dÃƒÆ\'Ã‚Â ng', 'đầy đủ')

# Write clean UTF-8
with open(home_file, 'w', encoding='utf-8') as f:
    f.write(text)

print('✓ Fixed home/index.html subtitle')
