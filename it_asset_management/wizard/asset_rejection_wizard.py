from odoo import models, fields


class AssetRejectionWizard(models.TransientModel):
    _name = "it.asset.rejection.wizard"
    _description = "IT Asset Request Rejection Wizard"

    request_id = fields.Many2one(
        comodel_name="it.asset.request",
        string="Request",
        required=True
    )

    rejection_reason = fields.Text(
        string="Rejection Reason",
        required=True
    )
    def action_confirm_rejection(self):
        self.ensure_one()
        self.request_id.write({
            "rejection_reason": self.rejection_reason,
        })
        self.request_id.action_reject()

        return {"type" : "ir.actions.act_window_close"}
