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
        # default=fields,
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