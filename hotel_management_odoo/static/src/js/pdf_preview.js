/** @odoo-module */

import {Dialog} from "@web/core/dialog/dialog";
import {_lt} from '@web/core/l10n/translation';
import {registry} from '@web/core/registry';
const { useEffect, onWillStart } = owl;

export class PdfPreviewDialog extends Dialog {
    setup() {
        super.setup();
        useEffect((modalEl) => {
            if (modalEl) {
                const modalHeader = modalEl.querySelector('.modal-header');
                const modalBody = modalEl.querySelector('.modal-body');
                const iframe = document.createElement("iframe");
                iframe.src = this._getSourceDocument();
                iframe.style.width = "100%";
                iframe.style.minHeight = "550px";
                modalBody.append(iframe);
            }
        }, () => [document.querySelector(':not(.o_inactive_modal).o_dialog')]);
    }

    _getSourceDocument() {
        console.log(this.props.srcurl);
        return "/web/static/lib/pdfjs/web/viewer.html?file="+this.props.srcurl;
    }
}

PdfPreviewDialog.props = {
    ...Dialog.props,
    srcurl: { type: String },
    close: Function,
};
delete PdfPreviewDialog.props.slots;


function getReportUrl({report_name, context, data}, env) {
    // Rough copy of action_service.js _getReportUrl method.
    let url = `/report/pdf/${report_name}`;
    const actionContext = context || {};
    if (data && JSON.stringify(data) !== "{}") {
        const encodedOptions = encodeURIComponent(JSON.stringify(data));
        const encodedContext = encodeURIComponent(JSON.stringify(actionContext));
        return `${url}?options=${encodedOptions}&context=${encodedContext}`;
    }
    if (actionContext.active_ids) {
        url += `/${actionContext.active_ids.join(",")}`;
    }
    const userContext = encodeURIComponent(JSON.stringify(env.services.user.context));
    return `${url}?context=${userContext}`;
}

async function _triggerDownload(action, options, env) {
    const url = getReportUrl(action, env)
    env.services.ui.block();
    try {
        env.services.dialog.add(PdfPreviewDialog, {
            srcurl: url,
            header: true,
            footer: false,
            title: _lt('ABC'),
            size: 'lg',
            withBodyPadding: false,
        });
    } finally {
        env.services.ui.unblock();
    }
    const onClose = options.onClose;
    if (action.close_on_report_download) {
        return env.services.action.doAction({ type: "ir.actions.act_window_close" }, { onClose });
    } else if (onClose) {
        onClose();
    }
}

registry.category("ir.actions.report handlers").add("og_pdf_preview_handler", async function (action, options, env) {
        if (action.report_type === "qweb-pdf") {
            await _triggerDownload(action, options, env);
            return true;
        }
        return false;
    });
