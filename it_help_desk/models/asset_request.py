from odoo import fields, models, api


class ItAssetRequest(models.Model):
    _inherit = "it.asset.request"

    # is_tech = fields.Boolean(string="Tech")

    def action_approve(self):
        result = super().action_approve()
        for request in self:
            if request.status == 'approved':
                existing_ticket = self.env['it.help.desk'].search([
                    ('request_id', '=', request.id)
                ], limit=1)

                if not existing_ticket:
                    self.env['it.help.desk'].sudo().create({
                        'request_id': request.id,
                    })

        return result


