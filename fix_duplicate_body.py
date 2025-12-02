# -*- coding: utf-8 -*-
"""
Fix duplicate </body> and </html> tags
"""

from pathlib import Path
import re

pages = [
    'manager', 'bots', 'create', 'rental', 'payment', 'commands', 
    'statistics', 'users', 'history', 'theme', 'settings', 'profile'
]

for page_name in pages:
    page_file = Path(f'web/{page_name}/index.html')
    
    if page_file.exists():
        with open(page_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix pattern: </body>\n</html>\n\n</body>\n</html>
        # Remove the second </body></html>
        fixed = re.sub(
            r'(</body>\s*\n\s*</html>)\s*\n\s*</body>\s*\n\s*</html>',
            r'\1',
            content
        )
        
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(fixed)
        
        print(f"✓ Fixed: {page_name}")

print("\n✅ All duplicate tags removed!")
