from odoo import fields, models, api

class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    is_technicians = fields.Boolean(string="Technician")

