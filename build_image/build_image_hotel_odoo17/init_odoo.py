import logging
_logger = logging.getLogger(__name__)

def setup_vietnamese(env):
    lang_code = 'vi_VN'
    
    # 1. Kích hoạt/Cài đặt Tiếng Việt
    _logger.info(f"Đang kiểm tra và kích hoạt ngôn ngữ: {lang_code}")
    lang_ids = env['res.lang'].search([('code', '=', lang_code)])
    if not lang_ids:
        env['res.lang']._activate_lang(lang_code)
        _logger.info("Đã kích hoạt Tiếng Việt.")
    else:
        lang_ids.write({'active': True})
        _logger.info("Tiếng Việt đã sẵn sàng.")

    # 2. Thiết lập ngôn ngữ mặc định cho Admin
    admin = env.ref('base.user_admin', raise_if_not_found=False)
    if admin:
        admin.write({'lang': lang_code})
        _logger.info("Đã đặt Tiếng Việt làm mặc định cho tài khoản Admin.")

    # 3. Commit thay đổi
    env.cr.commit()
    _logger.info("Cấu hình Odoo hoàn tất thành công.")

if __name__ == "__main__":
    setup_vietnamese(env)
