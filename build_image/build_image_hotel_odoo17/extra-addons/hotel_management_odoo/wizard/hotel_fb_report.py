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

class HotelFBReportWizard(models.TransientModel):
    _name = 'hotel.fb.report'
    _description = 'Báo cáo F&B chuyên sâu'

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
                'model': 'hotel.fb.report',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Bao cao F&B chuyen sau',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Báo cáo F&B')
        
        # Styles
        title_style = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
        header_style = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D3D3D3', 'align': 'center', 'valign': 'vcenter'})
        cell_style = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
        num_style = workbook.add_format({'border': 1, 'num_format': '#,##0', 'align': 'right', 'valign': 'vcenter'})
        
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 20)
        
        sheet.merge_range('A1:E1', 'BÁO CÁO PHÂN TÍCH F&B', title_style)
        sheet.merge_range('A2:E2', f"Từ ngày: {data['date_from']} - Đến ngày: {data['date_to']}", workbook.add_format({'align': 'center'}))
        
        # Table 1: Top Selling Items
        sheet.write(4, 0, 'PHẦN 1: TOP MÓN ĂN/ĐỒ UỐNG BÁN CHẠY', workbook.add_format({'bold': True, 'font_size': 12}))
        headers = ['STT', 'Tên món', 'Số lượng', 'Đơn giá TB', 'Thành tiền']
        for col, header in enumerate(headers):
            sheet.write(5, col, header, header_style)
            
        date_from = fields.Date.from_string(data['date_from'])
        date_to = fields.Date.from_string(data['date_to'])
        
        # Querying grouping by food_id
        query = """
            SELECT fbl.food_id, lp.name, SUM(fbl.uom_qty) as total_qty, AVG(fbl.price_unit) as avg_price, SUM(fbl.price_total) as total_amount
            FROM food_booking_line fbl
            JOIN room_booking rb ON fbl.booking_id = rb.id
            JOIN lunch_product lp ON fbl.food_id = lp.id
            WHERE rb.state IN ('check_in', 'done')
            AND rb.checkin_date <= %s
            AND rb.checkout_date >= %s
            GROUP BY fbl.food_id, lp.name
            ORDER BY total_qty DESC
        """
        self.env.cr.execute(query, (
            fields.Datetime.to_string(datetime.combine(date_to, datetime.max.time())),
            fields.Datetime.to_string(datetime.combine(date_from, datetime.min.time()))
        ))
        
        results = self.env.cr.dictfetchall()
        
        row = 6
        stt = 1
        grand_total = 0
        for res in results:
            sheet.write(row, 0, stt, cell_style)
            sheet.write(row, 1, res['name'], cell_style)
            sheet.write(row, 2, res['total_qty'], num_style)
            sheet.write(row, 3, res['avg_price'], num_style)
            sheet.write(row, 4, res['total_amount'], num_style)
            grand_total += res['total_amount']
            row += 1
            stt += 1
            
        sheet.write(row, 3, 'TỔNG CỘNG F&B:', workbook.add_format({'bold': True, 'align': 'right'}))
        sheet.write(row, 4, grand_total, workbook.add_format({'bold': True, 'num_format': '#,##0', 'border': 1}))
        
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
