/** @odoo-module **/

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";
import { isDragSourceExternalFile } from "@mail/utils/common/misc";
import { _t } from "@web/core/l10n/translation";   // 👈 add this


patch(Composer.prototype, {
    setup() {
        super.setup(...arguments);

        let model;

        model = this.props.composer?.thread?.model;
        this.isCrmLead = model === "crm.lead";

        console.log("📌 Final detected model:", model, "| isCrmLead:", this.isCrmLead);
    },



    onDropFile(ev) {
    // Detect if current composer model is crm.lead
    const model = this.props.composer?.thread?.model;
    console.log("Final detected model:", model);
    if (model === "crm.lead") {
        // 🚫 Block drag & drop
        this.env.services.notification.add(
            _t("Drag & drop file upload is disabled for CRM Leads."),
            { type: "warning" }
        );
        ev.preventDefault();
        return;
    }

    // ✅ Otherwise proceed normally
    if (isDragSourceExternalFile(ev.dataTransfer)) {
        for (const file of ev.dataTransfer.files) {
            this.attachmentUploader.uploadFile(file);
            console.log("Uploaded via drag & drop:", file.name);
        }
    }
}

});
