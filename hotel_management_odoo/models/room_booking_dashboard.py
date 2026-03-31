# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
import pytz

class RoomBooking(models.Model):
    _inherit = "room.booking"

    def get_details(self):
        """ Returns different counts for displaying in dashboard with optimized queries"""
        today = datetime.today()
        tz_name = self.env.user.tz or 'UTC'
        context_today = pytz.timezone('UTC').localize(today).astimezone(pytz.timezone(tz_name))
        today_start = datetime.combine(context_today.date(), datetime.min.time())
        today_end = datetime.combine(context_today.date(), datetime.max.time())

        total_room = self.env['hotel.room'].search_count([])
        check_in = self.env['room.booking'].search_count([('state', '=', 'check_in')])
        reservation = self.env['room.booking'].search_count([('state', '=', 'reserved')])
        
        check_out = self.env['room.booking.line'].search_count([
            ('checkout_date', '>=', today_start),
            ('checkout_date', '<=', today_end),
            ('booking_id.state', 'in', ['check_in', 'check_out', 'done'])
        ])

        staff_groups = [
            'hotel_management_odoo.hotel_group_admin',
            'hotel_management_odoo.cleaning_team_group_head',
            'hotel_management_odoo.cleaning_team_group_user',
            'hotel_management_odoo.hotel_group_reception',
            'hotel_management_odoo.maintenance_team_group_leader',
            'hotel_management_odoo.maintenance_team_group_user'
        ]
        group_ids = [self.env.ref(group).id for group in staff_groups if self.env.ref(group, raise_if_not_found=False)]
        staff = self.env['res.users'].search_count([('groups_id', 'in', group_ids)])

        total_vehicle = self.env['fleet.vehicle.model'].search_count([])
        available_vehicle = total_vehicle - self.env['fleet.booking.line'].search_count([('state', '=', 'check_in')])
        
        total_event = self.env['event.event'].search_count([])
        pending_events = self.env['event.event'].search_count([('date_end', '>=', fields.Datetime.now())])
        today_events = self.env['event.event'].search_count([
            ('date_end', '>=', today_start),
            ('date_end', '<=', today_end)
        ])

        food_items = self.env['lunch.product'].search_count([])
        food_order = self.env['food.booking.line'].search_count([
            ('booking_id.state', 'not in', ['check_out', 'cancel', 'done'])
        ])

        all_bookings = self.env['room.booking'].search([
            ('state', 'in', ['reserved', 'check_in', 'check_out', 'done'])
        ])
        
        total_revenue = sum(all_bookings.mapped('amount_total'))
        today_bookings = all_bookings.filtered(lambda b: b.date_order.date() == context_today.date())
        today_revenue = sum(today_bookings.mapped('amount_total'))
        pending_payment = sum(all_bookings.filtered(lambda b: b.state != 'done').mapped('amount_total'))

        available_room_ids = self.env['hotel.room'].search([('status', 'in', ['available', 'clean'])])
        occupied_count = total_room - len(available_room_ids)
        occupancy_rate = round((occupied_count / total_room) * 100, 2) if total_room > 0 else 0.0

        revenue_trend = []
        occupancy_trend = []
        labels = []
        
        start_date_7d = context_today.date() - timedelta(days=6)
        trend_bookings = all_bookings.filtered(lambda b: b.date_order.date() >= start_date_7d)
        
        # Batch fetch all room lines for the entire 7-day period to avoid N+1 queries
        trend_start_dt = datetime.combine(start_date_7d, datetime.min.time())
        trend_line_data = self.env['room.booking.line'].search([
            ('checkin_date', '<=', today_end),
            ('checkout_date', '>=', trend_start_dt),
            ('booking_id.state', 'in', ['reserved', 'check_in', 'done'])
        ])

        for i in range(6, -1, -1):
            date = context_today.date() - timedelta(days=i)
            labels.append(date.strftime('%d/%m'))
            day_rev = sum(trend_bookings.filtered(lambda b: b.date_order.date() == date).mapped('amount_total'))
            revenue_trend.append(round(day_rev, 2))
            
            d_start = datetime.combine(date, datetime.min.time())
            d_end = datetime.combine(date, datetime.max.time())
            
            # Filter in-memory instead of search_count in a loop
            occ_count = len(trend_line_data.filtered(lambda l: l.checkin_date <= d_end and l.checkout_date >= d_start))
            occupancy_trend.append(occ_count)

        today_room_revenue = 0.0
        active_booking_lines = self.env['room.booking.line'].search([
            ('booking_id.state', '=', 'check_in'),
            ('checkin_date', '<=', today_end),
            ('checkout_date', '>=', today_start)
        ])
        for line in active_booking_lines:
            days = line.uom_qty if line.uom_id.name in ['Ngày', 'Đêm'] else max(1, line.uom_qty / 24)
            if days > 0:
                today_room_revenue += (line.price_subtotal / days)

        adr = round(today_room_revenue / occupied_count, 2) if occupied_count > 0 else 0.0
        revpar = round(today_room_revenue / total_room, 2) if total_room > 0 else 0.0

        return {
            'total_room': total_room,
            'available_room': len(available_room_ids),
            'staff': staff,
            'check_in': check_in,
            'reservation': reservation,
            'check_out': check_out,
            'total_vehicle': total_vehicle,
            'available_vehicle': available_vehicle,
            'total_event': total_event,
            'today_events': today_events,
            'pending_events': pending_events,
            'food_items': food_items,
            'food_order': food_order,
            'total_revenue': round(total_revenue, 2),
            'today_revenue': round(today_revenue, 2),
            'pending_payment': round(pending_payment, 2),
            'occupancy_rate': occupancy_rate,
            'adr': adr,
            'revpar': revpar,
            'revenue_trend': revenue_trend,
            'occupancy_trend': occupancy_trend,
            'trend_labels': labels,
            'currency_symbol': self.env.company.currency_id.symbol,
            'currency_position': self.env.company.currency_id.position
        }

    @api.model
    def get_room_chart_data(self, floor_id=None, loaiphong_id=None, target_date=None):
        """
        Fetches room status counts and details for the 'Sơ đồ phòng' UI with optimized queries.
        """
        from datetime import datetime, time
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc

        if target_date:
            today_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            if today_date == fields.Date.today():
                now = fields.Datetime.now()
            else:
                local_dt = tz.localize(datetime.combine(today_date, time(14, 0)))
                now = local_dt.astimezone(pytz.utc).replace(tzinfo=None)
        else:
            today_date = fields.Date.today()
            now = fields.Datetime.now()

        room_domain = []
        if floor_id:
            room_domain.append(('floor_id', '=', int(floor_id)))
        if loaiphong_id and loaiphong_id != 'all':
            room_domain.append(('loaiphong_id', '=', int(loaiphong_id)))
            
        rooms = self.env['hotel.room'].search(room_domain)
        status_counts = self.env['hotel.room'].read_group(room_domain, ['status'], ['status'])
        counts_map = {res['status']: res['status_count'] for res in status_counts}
        
        arriving = 0
        departing = 0
        in_house = 0
        
        booking_lines = self.env['room.booking.line'].search([
            ('room_id', 'in', rooms.ids),
            ('booking_id.state', 'in', ['reserved', 'check_in']),
        ], order='checkin_date asc')
        
        room_to_booking = {}
        for line in booking_lines:
            if line.room_id.id not in room_to_booking:
                if line.checkin_date <= now and line.checkout_date > now:
                     room_to_booking[line.room_id.id] = line
                elif line.checkin_date > now and not room_to_booking.get(line.room_id.id):
                     room_to_booking[line.room_id.id] = line
        
        overstayers = booking_lines.filtered(lambda l: l.booking_id.state == 'check_in' and l.checkout_date <= now)
        for line in overstayers:
            if line.room_id.id not in room_to_booking:
                room_to_booking[line.room_id.id] = line

        room_data = []
        for room in rooms:
            active_booking_line = room_to_booking.get(room.id)
            booking_state = False
            is_departing = False
            local_checkin_date = False
            
            if active_booking_line:
                booking_state = active_booking_line.booking_id.state
                local_checkin_date = pytz.utc.localize(active_booking_line.checkin_date).astimezone(tz).date()
                
                if booking_state == 'reserved':
                    if local_checkin_date == today_date:
                        arriving += 1
                    elif target_date and local_checkin_date < today_date and active_booking_line.checkout_date > now:
                        in_house += 1
                        booking_state = 'check_in'
                
                elif booking_state == 'check_in':
                    in_house += 1
                    time_diff = active_booking_line.checkout_date - now
                    if time_diff.total_seconds() / 3600 <= 1:
                        departing += 1
                        is_departing = True

            visual_color = 'success'
            visual_icon = 'fa-bullseye'
            
            if is_departing:
                visual_color = 'danger'
                visual_icon = 'fa-walking fa-flip-horizontal'
            elif booking_state == 'check_in':
                visual_color = 'primary'
                visual_icon = 'fa-walking'
            elif booking_state == 'reserved':
                visual_color = 'info'
                visual_icon = 'fa-male'
            elif room.status == 'dirty':
                visual_color = 'warning'
                visual_icon = 'fa-wrench'
            elif room.status == 'repair':
                visual_color = 'secondary'
                visual_icon = 'fa-times'
            elif room.status in ['available', 'clean']:
                visual_color = 'success'
                visual_icon = 'fa-bullseye'

            room_data.append({
                'id': room.id,
                'name': room.name,
                'status': room.status,
                'room_type': room.room_type,
                'loaiphong': room.loaiphong_id.name,
                'floor_id': room.floor_id.id if room.floor_id else 0,
                'floor_name': room.floor_id.name if room.floor_id else 'Chưa cấp tầng',
                'booking_state': booking_state if (local_checkin_date and local_checkin_date <= today_date) else False,
                'is_departing': is_departing,
                'booking_id': active_booking_line.booking_id.id if active_booking_line else False,
                'visual_color': visual_color,
                'visual_icon': visual_icon,
            })

        return {
            'counts': {
                'total': len(rooms),
                'available': counts_map.get('available', 0),
                'clean': counts_map.get('clean', 0),
                'dirty': counts_map.get('dirty', 0),
                'repair': counts_map.get('repair', 0),
                'occupied': counts_map.get('occupied', 0),
                'arriving': arriving,
                'in_house': in_house,
                'departing': departing,
            },
            'rooms': room_data,
            'floors': [{'id': f.id, 'name': f.name} for f in self.env['hotel.floor'].search([])],
            'room_types': [('all', 'Tất cả')] + [(str(lp.id), lp.name) for lp in self.env['hotel.loaiphong'].search([])],
        }
