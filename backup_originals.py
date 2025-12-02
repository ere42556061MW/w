# -*- coding: utf-8 -*-
"""
Read garbled files properly and extract full page content
"""

import os
from pathlib import Path

# Create a backup directory for original files
backup_files = {
    'manager': 'web/manager/index.html',
    'bots': 'web/bots/index.html',
    'create': 'web/create/index.html',
    'rental': 'web/rental/index.html',
    'payment': 'web/payment/index.html',
    'commands': 'web/commands/index.html',
    'statistics': 'web/statistics/index.html',
    'users': 'web/users/index.html',
    'history': 'web/history/index.html',
    'theme': 'web/theme/index.html',
    'settings': 'web/settings/index.html',
    'profile': 'web/profile/index.html',
}

# First, let's make backups before we mess with the files
# Read each file with proper error handling
for page_name, file_path in backup_files.items():
    file_p = Path(file_path)
    if file_p.exists():
        try:
            with open(file_p, 'rb') as f:
                content_bytes = f.read()
            
            # Try to decode
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    text = content_bytes.decode(encoding)
                    # Check if we got some Vietnamese text
                    if 'Danh' in text or 'danh' in text or '>' in text:
                        backup_file = Path(f'backups/{page_name}_original.html')
                        backup_file.parent.mkdir(exist_ok=True)
                        with open(backup_file, 'w', encoding='utf-8') as bf:
                            bf.write(text)
                        print(f"✓ Backed up {page_name} with {encoding} encoding ({len(text)} bytes)")
                        break
                except:
                    continue
        except Exception as e:
            print(f"✗ Error backing up {page_name}: {e}")

print("\n✅ Backups created in 'backups' folder")
