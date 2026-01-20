/** @odoo-module **/
import { Link } from "@web_editor/js/wysiwyg/widgets/link";
import { patch } from "@web/core/utils/patch";
const originalApplyLinkToDom = Link.prototype.applyLinkToDom;

patch(Link.prototype, {
        _getData() {
        const originalData = super._getData;
        if (!originalData) return null;

        var isStickyButton = this._isStickyButton?.() || false;

        return {
            ...originalData,
            isStickyButton: isStickyButton,
        };
    },

applyLinkToDom(data) {
    const fields = super.applyLinkToDom;

    if (data.isStickyButton) {
    console.log('1')
        // Try to find closest <li> ancestor
        const liEl = this.$link.closest('li');
        const sectionEl = liEl.find('> div > section');
        console.log('Section:', sectionEl);

        if (liEl.length) {
        console.log('3')

            // Fix the <li> element position
            const rect = liEl[0].getBoundingClientRect();

            liEl.css({
                position: 'fixed',
                top: rect.top + 'px',
                left: (rect.left + 300) + 'px',
                width: rect.width + 'px',
                zIndex: 9999,
            });
        } else {
        console.log('4')
            // Fallback: fix only the link itself
            const el = this.$link[0];
            const rect = el.getBoundingClientRect();


            this.$link.css({
                position: 'fixed',
                top: rect.top + 'px',
                left: (rect.left + 50) + 'px',
                width: rect.width + 'px',
                zIndex: 9999,
            });
        }
    } else {
    console.log('2')
        // Reset styles for both li and link
        const liEl = this.$link.closest('li');
        if (liEl.length) {
            liEl.css({
                position: '',
                top: '',
                left: '',
                width: '',
                zIndex: '',
            });
        }
        this.$link.css({
            position: '',
            top: '',
            left: '',
            width: '',
            zIndex: '',
        });
    }

    return fields;
},


    _getIsStickyButton() {},
    _isStickyButton(){},

});