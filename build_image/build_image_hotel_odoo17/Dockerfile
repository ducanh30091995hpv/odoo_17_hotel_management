# Sử dụng base image Odoo 17 chính thức
FROM odoo:17.0

# Chuyển sang quyền root để cài đặt thêm thư viện và phân quyền
USER root

# Copy toàn bộ module custom vào thư mục addons của Odoo trong container
COPY ./extra-addons /mnt/extra-addons

# Copy file cấu hình vào container
COPY ./config/odoo.conf /etc/odoo/odoo.conf

# NEW: Copy các script hỗ trợ khởi tạo Tiếng Việt & Phân quyền
COPY ./init_odoo.py /tmp/init_odoo.py
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

# Cấp quyền thực thi cho entrypoint
RUN chmod +x /usr/local/bin/entrypoint.sh

# Chuyển lại về user odoo để đảm bảo bảo mật
USER odoo

# Thiết lập Entrypoint để xử lý khởi tạo ở lần đầu tiên
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Mặc định khởi động Odoo server với database odoo_db
CMD ["-d", "odoo_db"]