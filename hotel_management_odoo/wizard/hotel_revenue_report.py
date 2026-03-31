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

class HotelRevenueReportWizard(models.TransientModel):
    _name = 'hotel.revenue.report'
    _description = 'Báo cáo doanh thu chi tiết'

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
                'model': 'hotel.revenue.report',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Bao cao doanh thu chi tiet',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Doanh thu chi tiết')
        
        # Styles
        title_style = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
        header_style = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D3D3D3', 'align': 'center', 'valign': 'vcenter'})
        cell_style = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
        num_style = workbook.add_format({'border': 1, 'num_format': '#,##0', 'align': 'right', 'valign': 'vcenter'})
        footer_style = workbook.add_format({'bold': True, 'border': 1, 'num_format': '#,##0', 'align': 'right', 'bg_color': '#F2F2F2'})
        
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:G', 15)
        
        sheet.merge_range('A1:G1', 'BÁO CÁO DOANH THU CHI TIẾT', title_style)
        sheet.merge_range('A2:G2', f"Từ ngày: {data['date_from']} - Đến ngày: {data['date_to']}", workbook.add_format({'align': 'center'}))
        
        headers = ['STT', 'Ngày đến', 'Mã Folio', 'Nguồn khách', 'Tạm ứng', 'Tổng tiền', 'Còn lại']
        for col, header in enumerate(headers):
            sheet.write(3, col, header, header_style)
            
        date_from = fields.Date.from_string(data['date_from'])
        date_to = fields.Date.from_string(data['date_to'])
        
        bookings = self.env['room.booking'].search([
            ('state', 'in', ['check_in', 'done']),
            ('checkin_date', '<=', fields.Datetime.to_string(datetime.combine(date_to, datetime.max.time()))),
            ('checkout_date', '>=', fields.Datetime.to_string(datetime.combine(date_from, datetime.min.time())))
        ], order='checkin_date asc')
        
        row = 4
        stt = 1
        total_tratruoc = 0
        total_revenue = 0
        total_remain = 0
        
        for booking in bookings:
            sheet.write(row, 0, stt, cell_style)
            sheet.write(row, 1, booking.checkin_date.strftime('%d/%m/%Y') if booking.checkin_date else '', cell_style)
            sheet.write(row, 2, booking.name, cell_style)
            
            source_label = ''
            if booking.booking_source:
                source_label = dict(booking._fields['booking_source'].selection).get(booking.booking_source, '')
            sheet.write(row, 3, source_label, cell_style)
            
            sheet.write(row, 4, booking.tratruoc or 0, num_style)
            sheet.write(row, 5, booking.amount_total or 0, num_style)
            sheet.write(row, 6, (booking.amount_total - booking.tratruoc) or 0, num_style)
            
            total_tratruoc += booking.tratruoc
            total_revenue += booking.amount_total
            total_remain += (booking.amount_total - booking.tratruoc)
            
            row += 1
            stt += 1
            
        sheet.write(row, 3, 'TỔNG CỘNG:', workbook.add_format({'bold': True, 'align': 'right', 'border': 1}))
        sheet.write(row, 4, total_tratruoc, footer_style)
        sheet.write(row, 5, total_revenue, footer_style)
        sheet.write(row, 6, total_remain, footer_style)
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
