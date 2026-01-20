import { Component } from '@odoo/owl';
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WebsiteSale.include({
    /**
     * Trigger a state update of the ClickAndCollectAvailability component when the combination info
     * is updated.
     *
     * @override
     */
    _onChangeCombination(ev, $parent, combination) {
        const res = this._super.apply(this, arguments);
        var $crCount = $parent.find(".cr_count");

        const count = parseInt(combination.final_pricelists) || 0;

        if (count !== 0) {
            $crCount.show();
        } else {
            $crCount.hide();
        }

        return res;
    },
});
