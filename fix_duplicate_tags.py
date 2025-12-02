# -*- coding: utf-8 -*-
"""
Fix HTML pages - remove duplicate </section> tag
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
        
        # Remove duplicate </section> before <!-- Boxicons -->
        # Pattern: </section>\n</section>\n\n<!-- Boxicons
        fixed = re.sub(
            r'</section>\s*</section>\s*',
            '</section>\n',
            content
        )
        
        # Also fix double </body></html>
        fixed = re.sub(
            r'</body>\s*\n\s*</body>\s*\n\s*</html>',
            '</body>\n</html>',
            fixed
        )
        
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(fixed)
        
        print(f"✓ Fixed: {page_name}")

print("\n✅ All pages fixed!")
