# Sử dụng base image Odoo 17 chính thức
FROM odoo:17.0

# Chuyển sang quyền root để cài đặt thêm thư viện nếu cần
USER root

# Nếu module custom của bạn có file requirements.txt, hãy uncomment dòng dưới
# COPY ./extra-addons/my_module/requirements.txt /tmp/requirements.txt
# RUN pip install -r /tmp/requirements.txt

# Copy toàn bộ module custom vào thư mục addons của Odoo trong container
COPY ./extra-addons /mnt/extra-addons

# Copy file cấu hình vào container
COPY ./config/odoo.conf /etc/odoo/odoo.conf

# Chuyển lại về user odoo để đảm bảo bảo mật
USER odoo