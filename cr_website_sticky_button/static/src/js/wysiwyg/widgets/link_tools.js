/** @odoo-module **/
import { LinkTools } from "@web_editor/js/wysiwyg/widgets/link_tools";
import { patch } from "@web/core/utils/patch";

patch(LinkTools.prototype, {
    _getIsStickyButton(){
        return this.$el.find('we-checkbox[name="is_new_window"]').closest('we-row');
    },
    _isStickyButton(ev) {
        return this.$el.find('we-checkbox[name="is_sticky_button"]').closest('we-button.o_we_checkbox_wrapper').hasClass('active');
    },
    _onClickStickyCheckbox(ev){
        let value = this.stickyButton;
    }
});