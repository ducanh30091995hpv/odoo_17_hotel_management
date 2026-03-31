from odoo import api, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def get_branding_config(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        title = ir_config.get_param("web.base.title", "ADSMO")
        favicon = ir_config.get_param("web.base.favicon", False)
        return {
            'title': title,
            'favicon': favicon,
        }
