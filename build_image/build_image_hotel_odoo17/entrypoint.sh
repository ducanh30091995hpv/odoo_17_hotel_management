#!/bin/bash
set -e

# Kiểm tra nếu database chưa được khởi tạo thì thực hiện init
# Ở đây ta mặc định chạy init để đảm bảo Tiếng Việt luôn được nạp (Odoo sẽ tự bỏ qua nếu đã cài)
echo "----------------------------------------------------------------"
echo "BẮT ĐẦU QUÁ TRÌNH KHỞI TẠO HỆ THỐNG (TIẾNG VIỆT & PHÂN QUYỀN)"
echo "----------------------------------------------------------------"

# 1. Chạy Odoo để cài đặt các module và nạp Tiếng Việt (chỉ chạy 1 lần lúc đầu hoặc update)
odoo -d odoo_db -i hotel_management_odoo,web_admin_aurora,web_window_title --load-language=vi_VN --stop-after-init

# 2. Chạy script Python để thiết lập cấu hình người dùng Admin
echo "Đang cấu hình ngôn ngữ mặc định cho Admin..."
odoo shell -d odoo_db --noprompt < /tmp/init_odoo.py

echo "----------------------------------------------------------------"
echo "KHỞI TẠO HOÀN TẤT. ĐANG KHỞI ĐỘNG ODOO SERVER..."
echo "----------------------------------------------------------------"

# 3. Chạy lệnh gốc của Odoo
exec odoo "$@"
