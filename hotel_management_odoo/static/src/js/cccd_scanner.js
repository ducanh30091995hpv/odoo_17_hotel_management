/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CCCDScannerModal extends Component {
    static template = "hotel_management_odoo.CCCDScannerModal";
    static props = ["close", "res_id", "model"];

    setup() {
        this.state = useState({
            error: null,
            scanning: true,
        });
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        this.stream = null;
        this.detector = null;

        onMounted(() => {
            this.startCamera();
        });

        onWillUnmount(() => {
            this.stopCamera();
        });
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "environment" } 
            });
            const video = document.getElementById("cccd_video");
            if (video) {
                video.srcObject = this.stream;
                this.scanLoop();
            }
        } catch (err) {
            this.state.error = "Không thể truy cập camera. Vui lòng đảm bảo bạn đang dùng HTTPS và cấp quyền truy cập camera.";
            console.error(err);
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        this.state.scanning = false;
    }

    async scanLoop() {
        if (!this.state.scanning) return;

        const video = document.getElementById("cccd_video");
        if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) {
            requestAnimationFrame(() => this.scanLoop());
            return;
        }

        try {
            // Kiểm tra BarcodeDetector API (hỗ trợ Chrome/Edge/Android)
            if (window.BarcodeDetector) {
                if (!this.detector) {
                    this.detector = new window.BarcodeDetector({ formats: ['qr_code'] });
                }
                const barcodes = await this.detector.detect(video);
                if (barcodes.length > 0) {
                    this.onResult(barcodes[0].rawValue);
                    return;
                }
            } else {
                this.state.error = "Trình duyệt không hỗ trợ BarcodeDetector API. Vui lòng dùng Chrome hoặc trình duyệt dựa trên Chromium.";
                this.state.scanning = false;
                return;
            }
        } catch (err) {
            console.error("Scan error", err);
        }

        if (this.state.scanning) {
            requestAnimationFrame(() => this.scanLoop());
        }
    }

    async onResult(qrData) {
        this.stopCamera();
        this.state.scanning = false;
        
        try {
            const result = await this.orm.call(this.props.model, "process_cccd_data", [
                this.props.res_id,
                qrData
            ]);
            
            if (result && result.success) {
                this.notification.add(`Đã cập nhật thông tin: ${result.partner_name}`, {
                    type: "success",
                });
                // Reload form view
                window.location.reload(); 
            } else if (result && result.error) {
                this.state.error = result.error;
                this.state.scanning = true;
                this.startCamera();
            }
        } catch (err) {
            this.state.error = "Lỗi kết nối server khi xử lý CCCD.";
            this.state.scanning = true;
            this.startCamera();
        }
    }
}

const cccdScannerAction = (env, action) => {
    const { res_id, model } = action.params;
    const dialogService = env.services.dialog;
    dialogService.add(CCCDScannerModal, {
        res_id,
        model,
    });
};

registry.category("actions").add("cccd_scanner_action", cccdScannerAction);
