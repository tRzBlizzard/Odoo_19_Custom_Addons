from google.auth import default
from odoo.exceptions import ValidationError
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

    ticket_resolve_date = fields.Datetime(
        string='Estimated Resolve Date',
        # readonly=True,
    )

    description = fields.Text(
        string='Problem Description'
    )

    resolution_notes = fields.Text(
        string='Resolution Notes',
        tracking = True,
    )


    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('raised', 'Raised'),
            ('assigned', 'Assigned'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
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


    # assigned_technician = fields.Many2one(
    #     comodel_name='res.partner',
    #     string='Assigned Tech',
    #     domain="[('is_technicians', '=', True)]",
    #     tracking=True
    # )

    assigned_technician1 = fields.Many2one(
        comodel_name='res.users',
        string='Assigned Technician',
        domain=lambda self: [
            ('group_ids', 'in', [
                self.env.ref('it_help_desk.group_it_technician').id
            ])
        ],
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

    def action_assign(self):
        for ticket in self:
            if not ticket.assigned_technician1:
                raise ValidationError(
                    "You cannot move this ticket to In Progress without assigning a technician."
                )
            ticket.status = "assigned"

    def action_start_work(self):
        for ticket in self:
            if not ticket.ticket_resolve_date:
                raise ValidationError(
                    "You cannot Accept this ticket without adding an estimation date."
                )
            if ticket.assigned_technician1 != self.env.user:
                raise ValidationError(
                    "Only the assigned technician can start working on this ticket."
                )
            ticket.status = "assigned"
            ticket.status = "in_progress"

    def action_resolve(self):
        for ticket in self:
            if not ticket.resolution_notes:
                raise ValidationError(
                    "You cannot resolve this ticket without adding the resolution notes."
                )

            if ticket.assigned_technician1 != self.env.user:
                raise ValidationError(
                    "Only the assigned technician can resolve this ticket."
                )
            ticket.status = "resolved"

    def action_return_to_draft(self):
        for ticket in self:
            ticket.status = "draft"
