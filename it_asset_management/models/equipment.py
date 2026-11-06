from odoo import fields, models

class ItAssetEquipment(models.Model):
    _name = "it.asset.equipment"
    _description = "IT Equipment Catalogue"

    name = fields.Char(
        string="Equipment Name",
        required=True,
    )
    equipment_type = fields.Selection(
        selection=[
            ("gpu", "Graphics Card"),
            ("ssd", "SSD"),
            ("laptop", "Laptop"),
            ("desktop", "Desktop Computer"),
            ("monitor", "Monitor"),
        ],
        string="Equipment Type",
        required=True,
    )
    specifications = fields.Text(
        string="Specifications",

    )
    unit_price = fields.Float(
        string="Unit Price",
        required=True,
        default=0.0,
    )