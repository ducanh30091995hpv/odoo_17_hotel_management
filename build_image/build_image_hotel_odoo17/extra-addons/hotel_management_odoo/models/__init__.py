# -*- coding: utf-8 -*-
# 1. Base & Configuration
from . import hotel_settings
from . import hotel_holiday
from . import res_partner
from . import account_move
from . import account_move_line

# 2. Master Data (Rooms & Structure)
from . import hotel_floor
from . import loaiphong
from . import hotel_amenity
from . import hotel_room_equipment
from . import hotel_room_price_special
from . import hotel_room

# 3. Master Data (Services, Food, Fleet)
from . import hotel_service
from . import lunch_product
from . import fleet_vehicle_model
from . import hotel_phutroi
from . import hotel_phuthu

# 4. Main Models (Management)
from . import cleaning_team
from . import cleaning_request
from . import maintenance_team
from . import maintenance_request

# 5. Booking Base
from . import room_booking

# 6. Booking Lines (Depends on Booking and Master Data)
from . import room_booking_line
from . import service_booking_line
from . import food_booking_line
from . import fleet_booking_line
from . import event_booking_line
# Note: phutroi and phuthu booking lines
from . import phutroi_booking_line
from . import phuthu_booking_line

# 7. Booking Extensions (The Refactored Logic)
from . import room_booking_pricing
from . import room_booking_status
from . import room_booking_dashboard
from . import room_booking_zalo
from . import room_booking_ota
from . import room_booking_id
from . import room_booking_reporting
