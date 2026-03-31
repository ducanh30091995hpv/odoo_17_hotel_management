/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { SideBar } from "../sidebar/sidebar";
import { patch } from "@web/core/utils/patch";

patch(WebClient.components, {
    SideBar,
});
