from google.auth import default
from odoo import fields, models, api


class ItHelpDesk(models.Model):
    _name = 'it.help.desk'
    _description = 'Help Desk for IT Asset Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    ticket_number = fields.Char(
        string='Ticket Number',
        required=True,
        readonly=True,
        copy=False,
        index=True,
        default="New"
    )
    request_id = fields.Many2one(
        comodel_name='it.asset.request',
        string='Asset Request',
        required=True,
        readonly=True,
        ondelete='restrict',
        copy=False,
        tracking=True
    )

    ticket_generated_date = fields.Datetime(
        string='Ticket Generated On',
        required=True,
        readonly=True,
        default=fields.Datetime.now,
    )

    ticket_raised_date = fields.Datetime(
        string='Ticket Raised On',
        readonly=True,
    )

    description = fields.Text(
        string='Problem Description'
    )

    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('raised', 'Raised'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        #readonly=True,
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Low'),
            ('1', 'High'),
        ],
        string='Priority',
        default='0',
        tracking=True
    )
    assigned_technician = fields.Many2one(
        comodel_name='res.users',
        string='Assigned Technician',
        default='-',
        tracking=True,
    )

    faulty_line_ids = fields.Many2many(
        comodel_name='it.asset.request.line',
        string='Faulty Equipment',
        domain="[('request_id', '=', request_id)]",
    )

    issue_type = fields.Selection(
        selection=[
            ('hardware', 'Hardware Issue'),
            ('software', 'Software Issue'),
            ('performance', 'Performance Issue'),
            ('connectivity', 'Connectivity Issue'),
            ('physical_damage', 'Physical Damage'),
            ('other', 'Other'),
        ],
        string='Issue Type',
    )






    # Information Retrieved from Original Request
    request_number = fields.Char(
        related='request_id.request_number',
        string='Request Number',
        store=True
    )

    requester_id = fields.Many2one(
        related='request_id.requested_by',
        string='Requester',
        store=True
    )

    request_title = fields.Char(
        related='request_id.name',
        string='Request Title'
    )
    approver_id = fields.Many2one(
        related='request_id.approved_by',
        string='Approver',
        store=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("ticket_number", "New") == "New":
                vals["ticket_number"] = (
                        self.env["ir.sequence"].next_by_code("it.help.desk")
                        or "New"
                )

        return super().create(vals_list)


    def action_raise_ticket(self):
        for ticket in self:
            if ticket.status == "draft":
                # manager = request._get_it_asset_manager()
                ticket.ticket_raised_date = fields.Datetime.now()
                ticket.status = "raised"
                # template = self.env.ref(
                #     "it_asset_management.mail_template_it_asset_request_submitted"
                # )

                # template.send_mail(request.id, force_send=True)
