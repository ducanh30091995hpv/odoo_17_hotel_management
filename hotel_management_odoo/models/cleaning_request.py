# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnu K P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CleaningRequest(models.Model):
    """Class for creating and assigning Cleaning Request"""
    _name = "cleaning.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "sequence"
    _description = "Cleaning Request"

    sequence = fields.Char(string="Sequence", readonly=True, default='New',
                           copy=False, tracking=True,
                           help="Sequence for identifying the request")
    state = fields.Selection([('draft', 'Draft'),
                              ('assign', 'Assigned'),
                              ('ongoing', 'Cleaning'),
                              ('support', 'Waiting For Support'),
                              ('done', 'Completed')],
                             string="State",
                             default='draft', help="State of cleaning request")
    cleaning_type = fields.Selection(selection=[('room', 'Room'),
                                                ('hotel', 'Hotel'),
                                                ('vehicle', 'Vehicle')],
                                     required=True, tracking=True,
                                     string="Cleaning Type",
                                     help="Choose what is to be cleaned")
    room_id = fields.Many2one('hotel.room', string="Room",
                              help="Choose the room")
    hotel = fields.Char(string="Hotel", help="Cleaning request space in hotel")
    vehicle_id = fields.Many2one('fleet.vehicle.model',
                                 string="Vehicle",
                                 help="Cleaning request from vehicle")
    support_team_ids = fields.Many2many('res.users',
                                        string="Support Team",
                                        help="Support team members")
    support_reason = fields.Char(string='Support', help="Support Reason")
    description = fields.Char(string="Description",
                              help="Description about the cleaning")
    team_id = fields.Many2one('cleaning.team', string="Team",
                              required=True,
                              tracking=True,
                              help="Choose the team")
    head_id = fields.Many2one('res.users', string="Head",
                              related='team_id.team_head_id',
                              help="Head of cleaning team")
    assigned_id = fields.Many2one('res.users', string="Assigned To",
                                  help="The team member to whom the request is"
                                       "Assigned To")
    team_member_ids = fields.Many2many('res.users', compute='_compute_team_member_ids', store=False,
                                       help='For filtering Users')

    @api.depends('team_id')
    def _compute_team_member_ids(self):
        for record in self:
            if record.team_id:
                record.team_member_ids = record.team_id.member_ids.ids
            else:
                record.team_member_ids = []

    @api.model_create_multi
    def create(self, vals_list):
        """Sequence Generation"""
        for vals in vals_list:
            if vals.get('sequence', 'New') == 'New':
                vals['sequence'] = self.env['ir.sequence'].next_by_code(
                    'cleaning.request')
        return super().create(vals_list)

    def action_assign_cleaning(self):
        """Button action for updating the state to assign"""
        self.update({'state': 'assign'})

    def action_start_cleaning(self):
        """Button action for updating the state to ongoing"""
        self.write({'state': 'ongoing'})

    def action_done_cleaning(self):
        """Button action for updating the state to done and marking room as available"""
        self.write({'state': 'done'})
        if self.room_id:
            self.room_id.write({'status': 'available'})

    def action_assign_support(self):
        """Button action for updating the state to support"""
        if self.support_reason:
            self.write({'state': 'support'})
        else:
            raise ValidationError(_('Please enter the reason'))

    def action_assign_assign_support(self):
        """Button action for updating the state to ongoing"""
        if self.support_team_ids:
            self.write({'state': 'ongoing'})
        else:
            raise ValidationError(_('Please choose a support'))

    def action_maintain_request(self):
        """Button action for creating the maintenance request"""
        self.env['maintenance.request'].sudo().create({
            'date': fields.Date.today(),
            'state': 'draft',
            'type': self.cleaning_type,
            'vehicle_maintenance_id': self.vehicle_id.id
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': "Maintenance Request Sent Successfully",
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    @api.model
    def _cron_generate_stayover_cleaning(self):
        """
        Scheduled action to generate cleaning requests for rooms in 'check_in' state
        that have been occupied for at least one night and don't have a cleaning
        request for today yet.
        """
        config_obj = self.env['ir.config_parameter'].sudo()
        enable = config_obj.get_param('hotel_management_odoo.enable_stayover_cleaning')
        if not enable:
            return False

        team_id = int(config_obj.get_param('hotel_management_odoo.stayover_cleaning_team_id', 0))
        if not team_id:
            # Fallback to first available team if not configured
            team = self.env['cleaning.team'].search([], limit=1)
            if team:
                team_id = team.id
            else:
                return False

        today = fields.Date.today()
        # Find all active bookings
        active_bookings = self.env['room.booking'].search([('state', '=', 'check_in')])
        
        requests_created = 0
        for booking in active_bookings:
            for line in booking.room_line_ids:
                # 1. Check if check-in was before today (at least 1 night stay-over)
                if line.checkin_date.date() < today:
                    room = line.room_id
                    
                    # 2. Set Room Status to 'Dirty' (Automatically after each night)
                    if room.status != 'dirty':
                        room.write({'status': 'dirty'})
                    
                    # 3. Check if a cleaning request already exists for this room today
                    existing_request = self.search([
                        ('room_id', '=', room.id),
                        ('create_date', '>=', fields.Datetime.to_string(datetime.combine(today, datetime.min.time()))),
                        ('create_date', '<=', fields.Datetime.to_string(datetime.combine(today, datetime.max.time())))
                    ], limit=1)
                    
                    if not existing_request:
                        self.create({
                            'cleaning_type': 'room',
                            'room_id': room.id,
                            'team_id': team_id,
                            'description': _('Dọn phòng định kỳ cho khách ở lại (Stay-over) CV: %s') % booking.name,
                            'state': 'draft'
                        })
                        requests_created += 1
        
        return requests_created
