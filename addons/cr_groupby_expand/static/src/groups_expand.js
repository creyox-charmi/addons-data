/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments)

        // Auto-expand groups after the component is mounted
        onMounted(async () => {
            if (this.model.root.groupBy && this.model.root.groupBy.length > 0) {
                // Small delay to ensure everything is rendered
                setTimeout(async () => {
                    await this.expandlist();
                }, 5);
            }
        });
    },

    expandlist: async function () {
        try {
            var group = this.model.root.groups;
            if (!group || group.length === 0) return;

            for (let i = 0; i < group.length; i++) {
                if (group[i].isFolded) {
                    await group[i].toggle();
                }
                if (group[i].list?.model?.root?.groups?.[i]?.list?.model?.root?.groups?.[i]?.list?.groups) {
                    var groupOfList = group[i].list.model.root.groups[i].list.model.root.groups[i].list.groups;
                    await this._onClickChild(groupOfList);
                }
            }

            const expBtn = document.getElementsByClassName("exp-btn")[0];
            const cmpBtn = document.getElementsByClassName("cmp-btn")[0];
            if (expBtn) expBtn.classList.add('o_hidden');
            if (cmpBtn) cmpBtn.classList.remove('o_hidden');
        } catch (error) {
            console.error("Error expanding list:", error);
        }
    },

    compresslist: async function () {
        try {
            this.model.root.groups.forEach((el) => {
                if (!el.isFolded) {
                    el.toggle();
                }
            });

            const cmpBtn = document.getElementsByClassName("cmp-btn")[0];
            const expBtn = document.getElementsByClassName("exp-btn")[0];
            if (cmpBtn) cmpBtn.classList.add('o_hidden');
            if (expBtn) expBtn.classList.remove('o_hidden');
        } catch (error) {
            console.error("Error compressing list:", error);
        }
    },

    recursivelist: async function (groups) {
        groups.forEach((el) => {
            if (el.isFolded) {
                el.toggle();
            }

            if (el.list.groups) {
                if (el.list.groups.length > 0) {
                    this.recursivelist(el.list.groups);
                }
            }
        });
    },

    _onClickChild: async function (groupOfList) {
        if (groupOfList) {
            for (let j = 0; j < groupOfList.length; j++) {
                if (groupOfList[j].isFolded) {
                    await groupOfList[j].toggle();
                }
                if (groupOfList[j].list?.groups) {
                    await this._onClickChild(groupOfList[j].list.groups);
                }
            }
        }
    }
});