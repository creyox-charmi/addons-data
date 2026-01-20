/** @odoo-module **/
import { LinkDialog } from "@web_editor/js/wysiwyg/widgets/link_dialog";
import { patch } from "@web/core/utils/patch";

patch(LinkDialog.prototype, {
    start() {
        const fields = super.start;
        if (this.stickyButton) {
            this.$el.find('we-button.o_we_checkbox_wrapper').toggleClass('active', true);
        }
        return fields;
    },
    _getIsStickyButton() {
        return this.$el.find('input[name="is_sticky_button"]').closest('.row');
    },
    _isStickyButton() {
        return this.$el.find('input[name="is_sticky_button"]').prop('checked');
    }
});