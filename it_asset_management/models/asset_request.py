from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta
import re
# from tempfile import template


class ItAssetRequest(models.Model):
    _name = "it.asset.request"
    _description = "IT Equipment Request"
    _order = "id desc"
    _inherit = ["mail.thread"]

    name = fields.Char(
        string="Request Title",
        required=True,
        tracking=True,
    )

    phone = fields.Char(
        string="Phone Number",
        required=True,
        # tracking=True,
    )

    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested By",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    line_ids = fields.One2many(
        comodel_name="it.asset.request.line",
        inverse_name="request_id",
        string="Equipment Lines",
    )

    approved_by = fields.Many2one(
        comodel_name="res.users",
        string="Approved/Rejected By",
        readonly = True,
        copy=False,
        tracking=True,
    )

    rejection_reason = fields.Text(
        string="Reason for Rejection",
        readonly=True,
        copy=False,
        tracking=True,
    )

    # equipment_type = fields.Selection(
    #     selection=[
    #         ("laptop", "Laptop"),
    #         ("desktop", "Desktop Computer"),
    #         ("monitor", "Monitor"),
    #         ("gpu", "Graphics Card"),
    #         ("ssd", "SSD"),
    #     ],
    #     string="Equipment Type",
    #     required=True,
    #     tracking=True,
    # )

    # quantity = fields.Integer(
    #     string="Quantity",
    #     required=True,
    #     default=1,
    #     tracking=True,
    # )

    # unit_price = fields.Float(
    #     string="Unit Price",
    #     compute="_compute_prices",
    # )
    # total_price = fields.Float(
    #     string="Total Price",
    #     compute="_compute_prices",
    # )



    total_price = fields.Float(
        string="Total Price",
        compute="_compute_total_price",
        store=True,
    )

    @api.depends("line_ids.subtotal")
    def _compute_total_price(self):
        for request in self:
            request.total_price= sum(request.line_ids.mapped("subtotal"))




    # equipment_prices = {
    #     "laptop": 150000,
    #     "desktop": 120000,
    #     "monitor": 45000,
    #     "gpu": 80000,
    #     "ssd": 20000,
    # }
    reason = fields.Text(
        string="Reason for Request",
    )

    status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        required=True,
        default="draft",
        tracking=True,
    )
    request_number = fields.Char(
        string="Request Number",
        required=True,
        readonly=True,
        copy=False,
        index=True,
        default="New",
    )
    submission_datetime = fields.Datetime(
        string="Submission Date",
        # readonly=True,
        copy=False,
        tracking=True,
    )
    approve_reject_datetime = fields.Datetime(
        string="Approval/Rejection Date",
        # readonly=True,
        copy=False,
        tracking=True,
    )
    expected_date = fields.Datetime(
        string="Expected Date of Allocation",
        # readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("request_number", "New") == "New":
                vals["request_number"] = (
                        self.env["ir.sequence"].next_by_code("it.asset.request")
                        or "New"
                )

        return super().create(vals_list)

    # @api.depends("equipment_type", "quantity")
    # def _compute_prices(self):
    #     for request in self:
    #         request.unit_price = request.equipment_prices.get(
    #             request.equipment_type, 0
    #         )
    #         request.total_price = request.quantity * request.unit_price

    # @api.constrains("quantity")
    # def check_quantity(self):
    #     for request in self:
    #         if request.quantity > 10:
    #             raise ValidationError("Quantity can not exceed more than 10")
    # @api.constrains("quantity")
    # def check_quantity(self):
    #     for line in self:
    #         if line.quantity < 1 or line.quantity > 10:
    #             raise ValidationError(
    #                 "Quantity must be between 1 and 10."
    #             )

    @api.onchange('phone')
    def phone_on_change(self):
        if self.phone and (not self.phone.startswith("+923") or len(self.phone) != 13):
            return {
                "warning": {
                    "title": "Invalid Phone Number",
                    "message": "Use the format +923000000000."
                }
            }
        return None

    @api.constrains("phone")
    def check_phone(self):
        for request in self:
            if len(request.phone) != 13 or not request.phone.startswith("+923"):
                raise ValidationError("Invalid Phone Number, Use the format +923000000000.")

    def _get_it_asset_manager(self):
        self.ensure_one()

        team_member = self.env["crm.team.member"].search([
            ("user_id", "=", self.requested_by.id),
            ("crm_team_id.name", "=", "Sales"),
        ], limit=1)

        if not team_member:
            raise ValidationError(
                "The requester is not a member of the Sales team."
            )

        manager = team_member.crm_team_id.user_id

        if not manager:
            raise ValidationError(
                "The Sales team does not have a Team Leader assigned."
            )

        return manager

    def action_submit(self):
        for request in self:
            if request.status == "draft":
                manager = request._get_it_asset_manager()
                request.submission_datetime = fields.Datetime.now()
                request.status = "submitted"

                template = self.env.ref(
                    "it_asset_management.mail_template_it_asset_request_submitted"
                )

                template.send_mail(request.id, force_send=True)

    def action_approve(self):
        for request in self:
            if request.status == "submitted":
                request.approved_by = self.env.user
                request.approve_reject_datetime = fields.Datetime.now()
                request.expected_date = request.approve_reject_datetime + timedelta(days=7)
                request.status = "approved"

                template = self.env.ref(
                    "it_asset_management.mail_template_it_asset_request_decision"
                )
                template.send_mail(request.id, force_send=True, email_values={"email_to": request.requested_by.email},)

    def action_reject(self):
        for request in self:
            if request.status == "submitted":
                request.approved_by = self.env.user
                request.approve_reject_datetime = fields.Datetime.now()
                request.status = "rejected"

                template = self.env.ref(
                    "it_asset_management.mail_template_it_asset_request_decision"
                )
                template.send_mail(request.id, force_send=True, email_values={"email_to": request.requested_by.email},)

    def action_return_to_draft(self):
        for request in self:
            if request.status in ("approved", "rejected"):
                request.status = "draft"

    def action_open_rejection_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Reject IT Asset Request",
            "res_model": "it.asset.rejection.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_request_id": self.id,
            },
        }

