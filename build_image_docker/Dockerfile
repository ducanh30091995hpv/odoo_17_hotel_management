FROM odoo:17.0

USER root

# Install any additional dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy custom addons to the conventional path
COPY ./custom_addons /mnt/extra-addons

# Set permissions for the odoo user
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo
