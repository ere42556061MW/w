#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob

web_dir = r'c:\Users\vuhai\OneDrive\Máy tính\aaaas\web'
html_files = sorted(glob.glob(os.path.join(web_dir, '**', '*.html'), recursive=True))

# Vietnamese with diacritics → without diacritics
replacements = {
    'Quản Lý': 'Quan Ly',
    'Quản lý': 'Quan ly',
    'Quản': 'Quan',
    'Lý': 'Ly',
    'Zalo': 'Zalo',
    'mật': 'mat',
    'chế độ': 'che do',
    'đầy': 'day',
    'đủ': 'du',
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
    'Chậm': 'Cham',
    'Tắt': 'Tat',
    'Kích thước': 'Kich thuoc',
    'Kiểu chữ': 'Kieu chu',
    'Xem trước': 'Xem truoc',
    'Thẻ': 'The',
    'Nền': 'Nen',
    'Sáng': 'Sang',
    'Tối': 'Toi',
    'Tự động': 'Tu dong',
    'Bảng màu': 'Bang mau',
    'Chủ đạo': 'Chu dao',
    'Mặc định': 'Mac dinh',
    'Xanh dương': 'Xanh duong',
    'Xanh lá': 'Xanh la',
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
    'Lưu': 'Luu',
    'Lưu ý': 'Luu y',
    'Dự án': 'Du an',
    'Mới': 'Moi',
    'Cài': 'Cai',
    'Đặt': 'Dat',
    'Đặt lại': 'Dat lai',
}

fixed_count = 0

for fpath in html_files:
    if 'split_pages' in fpath:
        continue
    
    try:
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        original = text
        
        # Remove BOM
        if text.startswith('\ufeff'):
            text = text[1:]
        
        # Replace all diacritic Vietnamese with non-diacritic
        for diac, nodiac in replacements.items():
            text = text.replace(diac, nodiac)
        
        if text != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(text)
            page = os.path.basename(os.path.dirname(fpath)) or 'root'
            print(f'✓ {page}')
            fixed_count += 1
    
    except Exception as e:
        print(f'✗ {fpath}: {e}')

print(f'\n✓ Converted {fixed_count} files to non-diacritic Vietnamese')
