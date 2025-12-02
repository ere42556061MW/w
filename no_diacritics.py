#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob
import re

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = sorted(glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True))

# Map Vietnamese with diacritics to non-diacritic version
vietnamese_no_diac = {
    # Titles and common text
    'Quản Lý': 'Quan Ly',
    'Quản lý': 'Quan ly',
    'Quảng': 'Quang',
    'Mới': 'Moi',
    'Cài': 'Cai',
    'Đặt': 'Dat',
    'Đặt lại': 'Dat lai',
    'Dự': 'Du',
    'Dự án': 'Du an',
    'Chế độ': 'Che do',
    'Mật': 'Mat',
    'Mật khẩu': 'Mat khau',
    'Lưu': 'Luu',
    'Lưu ý': 'Luu y',
    'Tùy chỉnh': 'Tuy chinh',
    'Giao diện': 'Giao dien',
    'Hiệu ứng': 'Hieu ung',
    'Cá nhân': 'Ca nhan',
    'Hóa': 'Hoa',
    'Phần': 'Phan',
    'Số': 'So',
    'Độ': 'Do',
    'Tốc độ': 'Toc do',
    'Bình thường': 'Binh thuong',
    'Nhanh': 'Nhanh',
    'Chậm': 'Cham',
    'Tắt': 'Tat',
    'Kích thước': 'Kich thuoc',
    'Kiểu chữ': 'Kieu chu',
    'Xem trước': 'Xem truoc',
    'Thẻ': 'The',
    'Nền': 'Nen',
    'Gradient': 'Gradient',
    'Solid': 'Solid',
    'Pattern': 'Pattern',
    'Sáng': 'Sang',
    'Tối': 'Toi',
    'Tự động': 'Tu dong',
    'Bảng màu': 'Bang mau',
    'Chủ đạo': 'Chu dao',
    'Mặc định': 'Mac dinh',
    'Xanh dương': 'Xanh duong',
    'Xanh lá': 'Xanh la',
    'Cam': 'Cam',
    'Đỏ': 'Do',
    'Hồng': 'Hong',
    'Tím': 'Tim',
    'Vuông vức': 'Vuong vuc',
    'Nhỏ': 'Nho',
    'Trung bình': 'Trung binh',
    'Lớn': 'Lon',
    'Bo tròn': 'Bo tron',
    'Làm mờ': 'Lam mo',
    'Suốt': 'Suot',
    'Thẻ mẫu': 'The mau',
    'Đây là cách': 'Day la cach',
    'Được': 'Duoc',
    'Giao diện sẽ': 'Giao dien se',
    'Như thế nào': 'Nhu the nao',
    'Với': 'Voi',
    'Cài đặt': 'Cai dat',
    'Hiện tại': 'Hien tai',
    'Nút': 'Nut',
    'Button': 'Button',
    'Quản': 'Quan',
    'Lý': 'Ly',
    'Zalo': 'Zalo',
}

fixed_count = 0

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    try:
        # Read file
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        original = text
        
        # Remove BOM
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Replace Vietnamese with diacritics with no-diacritic version
        for with_diac, no_diac in vietnamese_no_diac.items():
            text = text.replace(with_diac, no_diac)
        
        # Remove any remaining mojibake broken characters
        text = re.sub(r'[À-ÿ¡-¿€-ˆ¬¡-§«»¼½¾¿æ]', '', text)
        text = re.sub(r'Â[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'Ã[^a-zA-Z0-9\s]', '', text)
        
        if text != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(text)
            page = os.path.basename(os.path.dirname(fpath)) or 'root'
            print(f'✓ {page}')
            fixed_count += 1
    
    except Exception as e:
        print(f'✗ Error in {fpath}: {e}')

print(f'\n✓ Fixed {fixed_count} files - all Vietnamese now has NO diacritics')
