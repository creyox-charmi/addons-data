/** @odoo-module **/

import { X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

console.log("=== Registering one2many_grouped / many2many_grouped widgets ===");

export class GroupedX2ManyField extends X2ManyField {
    setup() {
        super.setup();

        const fieldInfo = this.props.record.activeFields[this.props.name];
        let options = fieldInfo?.options;

        if (typeof options === "string") {
            try {
                options = JSON.parse(options.replace(/'/g, '"'));
            } catch (e) {
                console.error("Failed to parse options:", e);
                options = {};
            }
        }

        // Priority: options.groupBy > props.groupBy > context default_group_by
        this._groupByField = options?.groupBy || this.props.groupBy;

        // If not found, check context
        if (!this._groupByField && this.props.context?.default_group_by) {
            this._groupByField = this.props.context.default_group_by;
        }

        console.log("✓ GroupedX2ManyField setup with groupBy:", this._groupByField);
    }

const groups = Object.values(grouped).map(g => {
    // Create a proper list object with model reference
    const groupList = Object.create(list);
    groupList.records = g.records;
    groupList.isGrouped = false;
    groupList.groupBy = null;
    groupList.groupByField = null;
    groupList.groups = [];
    groupList.count = g.records.length;

    return {
        id: g.id,
        value: g.id,
        displayName: g.id,
        count: g.records.length,
        groupByField: g.groupByField,
        list: groupList,
        isFolded: false,
        toggle: function() {
            this.isFolded = !this.isFolded;
        },
        aggregates: {},
    };
});
    get list() {
        const list = super.list;

        if (!this._groupByField || !list) {
            return list;
        }

        // Don't re-group if already grouped
        if (list.isGrouped && list.groups && list.groups.length > 0) {
            console.log("✓ List already grouped, skipping");
            return list;
        }

        try {
            console.log("🔄 Attempting to group list by:", this._groupByField);

            // Try server-side groupBy first (if supported by the list model)
            if (typeof list.groupBy === "function") {
                console.log("📡 Using server-side groupBy");
                list.groupBy([this._groupByField]);
            }

            // If still not grouped, do client-side fallback
            if (!list.isGrouped || !list.groups || list.groups.length === 0) {
                console.log("🔧 Falling back to client-side grouping");
                this.groupListRecordsByField(list, this._groupByField);
            }
        } catch (err) {
            console.warn("⚠️ Grouping failed, using client-side fallback:", err);
            this.groupListRecordsByField(list, this._groupByField);
        }

        return list;
    }

    get rendererProps() {
        const props = super.rendererProps;

        if (this._groupByField && this.props.viewMode === "list") {
            props.archInfo = {
                ...props.archInfo,
                defaultGroupBy: [this._groupByField],
                activeActions: {
                    ...props.archInfo?.activeActions,
                    createGroup: true, // Enable group creation
                }
            };

            console.log("📋 RendererProps updated with groupBy:", this._groupByField);
        }

        return props;
    }
}

export const groupedX2ManyField = {
    component: GroupedX2ManyField,
    displayName: _t("Grouped Relational Table"),
    supportedTypes: ["one2many", "many2many"],
    useSubView: true,
    extractProps: (fieldInfo, dynamicInfo) => {
        let options = {};
        const attrs = fieldInfo.attrs || {};

        // Parse options attribute
        if (attrs.options) {
            try {
                options = typeof attrs.options === "string"
                    ? JSON.parse(attrs.options.replace(/'/g, '"'))
                    : attrs.options;
            } catch (e) {
                console.error("Failed to parse options:", e);
            }
        }

        // Extract groupBy from context if not in options
        if (!options.groupBy && dynamicInfo.context) {
            if (dynamicInfo.context.default_group_by) {
                options.groupBy = dynamicInfo.context.default_group_by;
            } else if (dynamicInfo.context.group_by) {
                // Handle both string and array formats
                const groupBy = dynamicInfo.context.group_by;
                options.groupBy = Array.isArray(groupBy) ? groupBy[0] : groupBy;
            }
        }

        const props = {
            addLabel: attrs["add-label"],
            context: dynamicInfo.context,
            domain: dynamicInfo.domain,
            crudOptions: options,
            string: fieldInfo.string,
            views: fieldInfo.views,
            viewMode: fieldInfo.viewMode,
            relatedFields: fieldInfo.relatedFields,
        };

        if (fieldInfo.widget) props.widget = fieldInfo.widget;
        if (options.groupBy) props.groupBy = options.groupBy;

        console.log("📦 Extracted props for grouped field:", props);
        return props;
    },
};

registry.category("fields").add("one2many_grouped", groupedX2ManyField);
registry.category("fields").add("many2many_grouped", groupedX2ManyField);

console.log("✓ one2many_grouped / many2many_grouped registered successfully");