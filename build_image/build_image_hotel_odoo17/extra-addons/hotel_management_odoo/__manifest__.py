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
{
    'name': 'Odoo17 Hotel Management',
    'version': '17.0.1.2.4',
    'category': 'Services',
    'summary': """Hotel Management, Odoo Hotel Management, Hotel, Room Booking odoo, Amenities Odoo, Event management, Rooms, Events, Food, Booking, Odoo Hotel, Odoo17, Odoo Apps""",
    'description': """The module helps you to manage rooms, amenities, 
     services, food, events and vehicles. End Users can book rooms and reserve 
     foods from hotel.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['account', 'event', 'fleet', 'lunch', 'sale_management', 'bus', 'mail'],
    'data': [
        'data/ir_data_donvitinh.xml',
        'data/hotel_phutroi.xml',
        'data/data_hotel.xml',
        'security/hotel_management_odoo_groups.xml',
        'security/hotel_management_odoo_security.xml',
        'security/ir.model.access.csv',
        'data/ir_data_sequence.xml',
        'data/housekeeping_cron.xml',
        'views/account_move_views.xml',
        'views/hotel_menu_views.xml',
        'views/res_config_settings_views.xml',
        'views/hotel_amenity_views.xml',
        'views/hotel_service_views.xml',
        'views/hotel_phutroi_views.xml',
        'views/hotel_floor_views.xml',
        'views/hotel_holiday_views.xml',
        'views/hotel_room_equipment_views.xml',
        'views/hotel_room_views.xml',
        'views/lunch_product_views.xml',
        'views/fleet_vehicle_model_views.xml',
        'views/room_booking_views.xml',
        'views/room_booking_line_views.xml',
        'views/maintenance_team_views.xml',
        'views/maintenance_request_views.xml',
        'views/cleaning_team_views.xml',
        'views/cleaning_request_views.xml',
        'views/food_booking_line_views.xml',
        'views/reporting_views.xml',
        'views/housekeeping_templates.xml',
        'wizard/room_booking_detail_views.xml',
        'wizard/sale_order_detail_views.xml',
        'wizard/early_checkout_wizard_views.xml',
        'wizard/hotel_stay_declaration_views.xml',
        'wizard/hotel_fb_report_views.xml',
        'report/in_bill.xml',
        'report/room_booking_reports.xml',
        'report/sale_order_reports.xml',
        'views/hotel_loaiphong_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hotel_management_odoo/static/src/js/action_manager.js',
            'hotel_management_odoo/static/src/css/dashboard.css',
            'hotel_management_odoo/static/src/components/rightbar/rightbar.js',
            'hotel_management_odoo/static/src/components/rightbar/rightbar.xml',
            'hotel_management_odoo/static/src/css/style.css',
            'hotel_management_odoo/static/src/image/clean-up.png',
            'hotel_management_odoo/static/src/image/checked.png',
            'hotel_management_odoo/static/src/image/customer.png',
            'hotel_management_odoo/static/src/image/repair-tools.png',
            'hotel_management_odoo/static/src/image/booking.png',
            'hotel_management_odoo/static/src/js/pdf_preview.js',
            'hotel_management_odoo/static/src/js/room_chart.js',
            'hotel_management_odoo/static/src/xml/room_chart.xml',
            'hotel_management_odoo/static/src/js/cccd_scanner.js',
            'hotel_management_odoo/static/src/xml/cccd_scanner.xml',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
