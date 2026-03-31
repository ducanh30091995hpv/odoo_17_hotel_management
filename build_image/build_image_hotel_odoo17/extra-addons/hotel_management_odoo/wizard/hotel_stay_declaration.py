# -*- coding: utf-8 -*-
from datetime import datetime
import io
import json
from odoo import fields, models, _, api
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class HotelStayDeclarationWizard(models.TransientModel):
    _name = 'hotel.stay.declaration'
    _description = 'Khai báo tạm trú'

    date_from = fields.Date(string='Từ ngày', default=fields.Date.context_today, required=True)
    date_to = fields.Date(string='Đến ngày', default=fields.Date.context_today, required=True)

    def action_export_xlsx(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'hotel.stay.declaration',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Khai bao tam tru',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Khai báo tạm trú')
        
        # Styles
        title_style = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
        header_style = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D3D3D3', 'align': 'center'})
        cell_style = workbook.add_format({'border': 1, 'align': 'left'})
        date_cell_style = workbook.add_format({'border': 1, 'align': 'center'})
        
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 15)
        sheet.set_column('E:E', 20)
        sheet.set_column('G:I', 15)
        
        sheet.merge_range('A1:I1', 'DANH SÁCH KHÁCH KHAI BÁO TẠM TRÚ', title_style)
        sheet.merge_range('A2:I2', f"Từ ngày: {data['date_from']} - Đến ngày: {data['date_to']}", workbook.add_format({'align': 'center'}))
        
        headers = ['STT', 'Họ và tên', 'Ngày sinh', 'Giới tính', 'Số CCCD/Hộ chiếu', 'Quốc tịch', 'Ngày đến', 'Ngày đi', 'Phòng']
        for col, header in enumerate(headers):
            sheet.write(3, col, header, header_style)
        
        # Data Retrieval
        date_from = fields.Date.from_string(data['date_from'])
        date_to = fields.Date.from_string(data['date_to'])
        
        # Filter bookings that are active during the period
        bookings = self.env['room.booking'].search([
            ('state', 'in', ['check_in', 'done']),
            ('checkin_date', '<=', fields.Datetime.to_string(datetime.combine(date_to, datetime.max.time()))),
            ('checkout_date', '>=', fields.Datetime.to_string(datetime.combine(date_from, datetime.min.time())))
        ])
        
        row = 4
        stt = 1
        for booking in bookings:
            for line in booking.room_line_ids:
                # Add main guest and extra guests
                all_guests = []
                if line.partner_id:
                    all_guests.append(line.partner_id)
                for guest in line.extra_guest_ids:
                    if guest not in all_guests:
                        all_guests.append(guest)
                
                for guest in all_guests:
                    sheet.write(row, 0, stt, cell_style)
                    sheet.write(row, 1, guest.name or '', cell_style)
                    sheet.write(row, 2, guest.birthdate_date.strftime('%d/%m/%Y') if guest.birthdate_date else '', date_cell_style)
                    
                    gender_label = ''
                    if guest.gender:
                        gender_label = dict(guest._fields['gender'].selection).get(guest.gender, '')
                    sheet.write(row, 3, gender_label, cell_style)
                    
                    sheet.write(row, 4, guest.cccd_number or '', cell_style)
                    sheet.write(row, 5, guest.country_id.name or 'Việt Nam', cell_style)
                    sheet.write(row, 6, line.checkin_date.strftime('%d/%m/%Y %H:%M') if line.checkin_date else '', date_cell_style)
                    sheet.write(row, 7, line.checkout_date.strftime('%d/%m/%Y %H:%M') if line.checkout_date else '', date_cell_style)
                    sheet.write(row, 8, line.room_id.name or '', cell_style)
                    row += 1
                    stt += 1
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
