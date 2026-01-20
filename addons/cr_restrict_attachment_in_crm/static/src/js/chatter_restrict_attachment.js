/** @odoo-module **/

import { Chatter } from "@mail/chatter/web_portal/chatter";
import { useCustomDropzone } from "@web/core/dropzone/dropzone_hook";
import { MailAttachmentDropzone } from "@mail/core/common/mail_attachment_dropzone";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        const notification = useService("notification"); // get Odoo notification service

        useCustomDropzone(this.rootRef, MailAttachmentDropzone, {
            extraClass: "o-mail-Chatter-dropzone",
            onDrop: async (ev) => {
                const model = this.state.thread?.model || this.props.webRecord?.model;

                if (model === "crm.lead") {
                    ev.preventDefault();

                    // Show user-friendly warning
                    notification.add(
                        "Attachment upload is disabled for CRM Leads.",
                        { type: "warning" }
                    );
                    return;
                }


                if (!this.state.thread?.id) {
                    const saved = await this.props.saveRecord?.();
                    if (!saved) {
                        console.warn("❌ Record not saved, cancelling drop");
                        return;
                    }
                }

                const files = [...ev.dataTransfer.files];

                await Promise.all(files.map((file) =>
                    this.attachmentUploader.uploadFile(file)
                ));

                if (this.props.hasParentReloadOnAttachmentsChanged) {
                    this.reloadParentView();
                }

                this.state.isAttachmentBoxOpened = true;
            }
        });
    }
});


