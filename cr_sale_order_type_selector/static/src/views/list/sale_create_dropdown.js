/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {

    async onClickCreate(event) {
        console.log("=== onClickCreate triggered ===");
        console.log("Model:", this.model.config.resModel);

        if (this.model.config.resModel === "sale.order") {
            event.stopPropagation();
            event.preventDefault();

            const self = this;

            // Create dropdown dynamically
            const button = event.currentTarget;
            const dropdownMenu = document.createElement("ul");
            dropdownMenu.className = "dropdown-menu show custom-dropdown-menu";
            dropdownMenu.style.position = "absolute";

            const createOption = (label, orderType) => {
                const li = document.createElement("li");
                const a = document.createElement("a");
                a.href = "#";
                a.className = "dropdown-item";
                a.innerText = label;
                a.onclick = (e) => {
                    e.preventDefault();
                    console.log(label + " clicked");

                    // Use action service instead of trigger_up
                    self.env.services.action.doAction({
                        type: "ir.actions.act_window",
                        res_model: "sale.order",
                        views: [[false, "form"]],
                        target: "current",
                        context: { ...self.env.context, default_td_order_type: orderType },
                    });

                    dropdownMenu.remove();
                };
                li.appendChild(a);
                return li;
            };

            dropdownMenu.appendChild(createOption("B2B (Kronos)", "kronos"));
            dropdownMenu.appendChild(createOption("B2C (Kronos Lab)", "kronos_lab"));

            // Remove any previous dropdown
            const existing = document.querySelector(".custom-dropdown-menu");
            if (existing) existing.remove();

            // Position dropdown below the button
            const rect = button.getBoundingClientRect();
            dropdownMenu.style.top = rect.bottom + window.scrollY + "px";
            dropdownMenu.style.left = rect.left + window.scrollX + "px";
            dropdownMenu.style.zIndex = 9999;

            document.body.appendChild(dropdownMenu);

            // Remove dropdown if clicked outside
            const closeDropdown = (e) => {
                if (!dropdownMenu.contains(e.target)) {
                    dropdownMenu.remove();
                    document.removeEventListener("click", closeDropdown);
                }
            };
            document.addEventListener("click", closeDropdown);

            console.log("Dropdown displayed");
        } else {
            // fallback to default behavior for other models
            return super.onClickCreate(event);
        }
    },
});
