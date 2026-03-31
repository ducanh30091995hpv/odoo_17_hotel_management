# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

CONFIG_PARAM_WEB_WINDOW_TITLE = "web.base.title"

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    web_window_title = fields.Char('Window Title')
    web_favicon = fields.Binary('Window Favicon', help="Select an image to use as favicon")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        web_window_title = ir_config.get_param(CONFIG_PARAM_WEB_WINDOW_TITLE, default='')
        web_favicon = ir_config.get_param("web.base.favicon", default=False)
        res.update(
            web_window_title=web_window_title,
            web_favicon=web_favicon
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param(CONFIG_PARAM_WEB_WINDOW_TITLE, self.web_window_title or "")
        ir_config.set_param("web.base.favicon", self.web_favicon or False)
