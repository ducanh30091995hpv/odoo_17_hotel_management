/** @odoo-module alias=web.window.title **/

import { WebClient } from "@web/webclient/webclient";
import {patch} from "@web/core/utils/patch";

patch(WebClient.prototype, {
    setup() {
        const customTitle = document.title;
        super.setup();
        this.title.setParts({ zopenerp: customTitle });
    }
});
