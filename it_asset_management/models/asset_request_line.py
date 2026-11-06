from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ItAssetRequestLine(models.Model):
    _name = "it.asset.request.line"
    _description = "IT Equipment Request Line"

    request_id = fields.Many2one(
        comodel_name="it.asset.request",
        string = "Equipment Request",
        required=True,
        ondelete="cascade",
    )
    equipment_id = fields.Many2one(
        comodel_name="it.asset.equipment",
        string="Equipment",
        required=True,
    )

    quantity = fields.Integer(
        string="Quantity",
        required=True,
        default=1,
    )

    unit_price = fields.Float(
        string="Unit Price",
        related="equipment_id.unit_price",
        store=True,
        readonly=True,
    )

    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
    )

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.constrains("quantity")
    def check_quantity(self):
        for line in self:
            if line.quantity < 1 or line.quantity > 10:
                raise ValidationError(
                    "Quantity must be between 1 and 10."
                )