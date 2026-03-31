# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _render_template(self, template, values=None):
        if template in ['web.login', 'web.webclient_bootstrap']:
            if not values:
                values = {}
            ir_config = self.env['ir.config_parameter'].sudo()
            values["title"] = ir_config.get_param("web.base.title", "ADSMO") or "ADSMO"
            favicon = ir_config.get_param("web.base.favicon", "")
            if favicon:
                values["x_icon"] = f"data:image/x-icon;base64,{favicon}"
        return super(View, self)._render_template(template, values)
