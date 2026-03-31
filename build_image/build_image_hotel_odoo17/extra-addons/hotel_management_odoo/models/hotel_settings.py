# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
import requests

class HotelConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def get_hour_24h(self):
        selection = []
        for i in range(1, 25, 1):
            selection += [('%s' % i, '%sh' % i)]
        return selection
    def get_tennganhang(self):
        selection = []
        URL = "https://api.vietqr.io/v2/banks"
        r = requests.get(url=URL)
        data = r.json()
        for i in data['data']:
            selection += [('%s' % i['bin'], '%s' % i['shortName'] + " | " + i['name'])]
        return selection
    def get_minute(self):
        selection = []
        for i in range(1, 60, 1):
            selection += [('%s' % i, '%sp' % i)]
        return selection

    username_booking_com = fields.Char(string='Tên đăng nhập',help="Tên đăng nhập",config_parameter='hotel_management_odoo.username_booking_com',default='Tên đăng nhập')
    password_booking_com = fields.Char(string='Mật khẩu',help="Mật khẩu",config_parameter='hotel_management_odoo.password_booking_com',default='Mật khẩu')
    username_expedia = fields.Char(string='Tên đăng nhập',help="Tên đăng nhập",config_parameter='hotel_management_odoo.username_expedia',default='Tên đăng nhập')
    password_expedia = fields.Char(string='Mật khẩu',help="Mật khẩu",config_parameter='hotel_management_odoo.password_expedia',default='Mật khẩu')

    loichaochantrang_bill = fields.Char(string='Lời chào chân trang',help="Lời chào chân trang", config_parameter='hotel_management_odoo.loichaochantrang_bill', default='Hẹn gặp lại quý khách!')
    sotaikhoannganhang = fields.Char(string='Số tài khoản ngân hàng',help="Số tài khoản ngân hàng", config_parameter='hotel_management_odoo.sotaikhoannganhang')
    tennganhang = fields.Selection(get_tennganhang, string='Tên ngân hàng',
                                             help="Tên ngân hàng",
                                             config_parameter='hotel_management_odoo.tennganhang')
    nghi_ngay_qua_tieng_le_tinh_them_tieng_khong_tinh_thanh_1_ngay = fields.Boolean(
        "Nếu khách nghỉ ngày quá tiếng lẻ sẽ tính thêm tiếng lẻ không tính thành một ngày",
        config_parameter='hotel_management_odoo.nghi_ngay_qua_tieng_le_tinh_them_tieng_khong_tinh_thanh_1_ngay')
    so_tien_ap_dung = fields.Integer('Số tiền áp dụng', config_parameter='hotel_management_odoo.so_tien_ap_dung', default=80000)

    tinh_tien_cac_tieng_mac_dinh_ap_dung_sau_2h_dau = fields.Boolean(
        "Cho phép tính tiền các tiếng mặc định áp dụng cho các phòng sau 2h đầu",
        config_parameter='hotel_management_odoo.tinh_tien_cac_tieng_mac_dinh_ap_dung_sau_2h_dau')
    so_tien_ap_dung_tieng_thu_3 = fields.Integer('Số tiền áp dụng tiếng thứ 3', config_parameter='hotel_management_odoo.so_tien_ap_dung_tieng_thu_3', default=20000)
    khong_tinh_tien_phong_voi_hoa_don_time_khong_qua = fields.Boolean(
        "Không tính tiền phòng đối với các hóa đơn ở với thời gian không quá.",
        config_parameter='hotel_management_odoo.khong_tinh_tien_phong_voi_hoa_don_time_khong_qua')
    so_phut_khong_tinh_tien = fields.Integer(
        'Số phút tối thiểu để bắt đầu tính tiền',
        config_parameter='hotel_management_odoo.so_phut_khong_tinh_tien',
        default=30,
        help="Nếu khách ở dưới số phút này, hệ thống sẽ không tính tiền phòng. Áp dụng khi 'Không tính tiền phòng với hóa đơn thời gian không quá' được bật."
    )
    tinh_phu_troi_neu_qua_gio_checkin_checkout = fields.Boolean(
        "Chỉ bắt đầu tính phụ trội nếu quá giờ Checkin hoặc Checkout.",
        config_parameter='hotel_management_odoo.tinh_phu_troi_neu_qua_gio_checkin_checkout')
    lam_tron_time_neu_qua = fields.Selection(get_minute, string='Làm tròn thời gian nếu quá',
                                             default='15',
                                             help="Làm tròn thời gian nếu quá",
                                             config_parameter='hotel_management_odoo.lam_tron_time_neu_qua')
    tudong_ngay_neu_tien_quadem_hoac_gio_lon_hon_tien_ngay = fields.Boolean(
        "Tự động chọn Theo Ngày nếu số tiền Qua Đêm hoặc Theo Giờ lớn hơn số tiền Theo Ngày",
        config_parameter='hotel_management_odoo.tudong_ngay_neu_tien_quadem_hoac_gio_lon_hon_tien_ngay')
    tu_dong_qua_dem_neu_so_tien_gio_lon_hon_so_tien_qua_dem = fields.Boolean(
        "Tự động chọn Qua đêm nếu số tiền ở giờ lớn hơn số tiền ở Qua đêm",
        config_parameter='hotel_management_odoo.tu_dong_qua_dem_neu_so_tien_gio_lon_hon_so_tien_qua_dem')
    tu_dong_qua_dem_khach_checkin_qua_dem_va_o_qua_so_tieng = fields.Boolean(
        "Tự động chọn Qua đêm nếu khách Checkin trong khung giờ qua đêm và ở quá từ số tiếng",
        config_parameter='hotel_management_odoo.tu_dong_qua_dem_khach_checkin_qua_dem_va_o_qua_so_tieng')
    mot_ngay_du_24h = fields.Boolean("Một ngày đủ 24 tiếng", config_parameter='hotel_management_odoo.mot_ngay_du_24h', default=True)
    so_gio_1_ngay = fields.Integer(
        'Nếu không đủ 24h, 1 ngày được tính là bao nhiêu giờ',
        config_parameter='hotel_management_odoo.so_gio_1_ngay',
        default=12,
        help="Áp dụng khi 'Một ngày đủ 24 tiếng' bị tắt. Ví dụ: 12 có nghĩa là check-in 14:00 và check-out trước 14:00 hôm sau = 1 ngày."
    )
    tu_dong_gio = fields.Selection(get_hour_24h, string='Tự động chọn Qua đêm nếu khách Nhận Phòng sau thời điểm giờ',
                                   default='12',
                                   help="Tự động chọn Qua đêm nếu khách Nhận Phòng sau thời điểm giờ",
                                   config_parameter='hotel_management_odoo.tu_dong_gio')
    tu_dong_phut = fields.Selection(get_minute, string='Tự động chọn Qua đêm nếu khách Nhận Phòng sau thời điểm phút',
                                    default='15',
                                    help="Tự động chọn Qua đêm nếu khách Nhận Phòng sau thời điểm phút",
                                    config_parameter='hotel_management_odoo.tu_dong_phut')
    tu_dong_tra_gio = fields.Selection(get_hour_24h,
                                       string='Tự động chọn Qua đêm nếu khách Trả Phòng sau thời điểm giờ',
                                       default='12',
                                       help="Tự động chọn Qua đêm nếu khách Trả Phòng sau thời điểm giờ",
                                       config_parameter='hotel_management_odoo.tu_dong_tra_gio')
    tu_dong_tra_phut = fields.Selection(get_minute,
                                        string='Tự động chọn Qua đêm nếu khách Trả Phòng sau thời điểm phút',
                                        default='15',
                                        help="Tự động chọn Qua đêm nếu khách Trả Phòng sau thời điểm phút",
                                        config_parameter='hotel_management_odoo.tu_dong_tra_phut')
    tu_dong_chon_qua_dem_khi_nhan_phong = fields.Boolean("Tự động chọn Qua đêm nếu khách Nhận Phòng sau thời điểm",
                                                         config_parameter='hotel_management_odoo.tu_dong_chon_qua_dem_khi_nhan_phong')
    tu_dong_chon_qua_dem_khi_tra_phong = fields.Boolean("Tự động chọn Qua đêm nếu khách Trả Phòng sau thời điểm",
                                                        config_parameter='hotel_management_odoo.tu_dong_chon_qua_dem_khi_tra_phong')
    va_tra_phong_truoc = fields.Selection(get_hour_24h, string='Và trả phòng trước xH hôm sau',
                                          default='12',
                                          help="Và trả phòng trước xH hôm sau",
                                          config_parameter='hotel_management_odoo.va_tra_phong_truoc')
    nhan_phong_den_truoc = fields.Selection(get_hour_24h, string='Nhận phòng đến trước',
                                            default='18',
                                            help="Nhận phòng đến trước",
                                            config_parameter='hotel_management_odoo.nhan_phong_den_truoc')
    nhan_phong_tu = fields.Selection(get_hour_24h, string='Nhận phòng từ',
                                     default='18',
                                     help="Nhận phòng từ",
                                     config_parameter='hotel_management_odoo.nhan_phong_tu')
    checkin_checkout_cung_ngay = fields.Selection([
        ('1', 'Mặc định'),
        ('2', 'Tách phụ trội'),
        ('3', 'Luôn chỉ tính 1 ngày')],
        string='Khách Checkin và Checkout trong cùng 1 ngày được tính',
        default='1',
        help="Khách Checkin và Checkout trong cùng 1 ngày được tính",
        config_parameter='hotel_management_odoo.checkin_checkout_cung_ngay')
    gio_tra_phong = fields.Selection(get_hour_24h, string='Giờ trả phòng',
                                     default='12',
                                     help="Giờ trả phòng của khách sạn",
                                     config_parameter='hotel_management_odoo.gio_tra_phong')
    gio_nhan_phong = fields.Selection(get_hour_24h, string='Giờ nhận phòng',
                                      default='12',
                                      help="Giờ nhận phòng của khách sạn",
                                      config_parameter='hotel_management_odoo.gio_nhan_phong')

    # Zalo ZNS / SMS Configuration
    enable_zalo_notification = fields.Boolean(string='Bật thông báo Zalo ZNS', config_parameter='hotel_management_odoo.enable_zalo_notification')
    zalo_oa_id = fields.Char(string='Zalo OA ID', config_parameter='hotel_management_odoo.zalo_oa_id')
    zalo_access_token = fields.Char(string='Zalo Access Token', config_parameter='hotel_management_odoo.zalo_access_token')
    zalo_template_reserved = fields.Char(string='ZNS Template (Reserved)', config_parameter='hotel_management_odoo.zalo_template_reserved')
    zalo_template_checkout = fields.Char(string='ZNS Template (Checkout)', config_parameter='hotel_management_odoo.zalo_template_checkout')

    # PayOS Configuration
    payos_client_id = fields.Char(string='PayOS Client ID', config_parameter='hotel_management_odoo.payos_client_id')
    payos_api_key = fields.Char(string='PayOS API Key', config_parameter='hotel_management_odoo.payos_api_key')
    payos_checksum_key = fields.Char(string='PayOS Checksum Key', config_parameter='hotel_management_odoo.payos_checksum_key')

    # Stay-over Housekeeping Configuration
    enable_stayover_cleaning = fields.Boolean(string='Bật dọn phòng tự động (Stay-over)', config_parameter='hotel_management_odoo.enable_stayover_cleaning', help="Tự động tạo yêu cầu dọn phòng định kỳ cho khách ở lại.")
    stayover_cleaning_team_id = fields.Many2one('cleaning.team', string='Đội dọn dẹp mặc định (Stay-over)', config_parameter='hotel_management_odoo.stayover_cleaning_team_id', help="Đội dọn dẹp sẽ được chỉ định cho các yêu cầu tự động.")


