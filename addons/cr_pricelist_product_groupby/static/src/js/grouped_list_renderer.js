/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";

console.log("🚀 [MODULE LOAD] grouped_x2many_field.js is loading...");

patch(ListRenderer.prototype, {
        setup() {
        super.setup();
        console.log("🎯 [ListRenderer.setup] PATCHED setup called");
        console.log("📦 Props received:", this.props);
        this.activeActions;
        this.canCreateGroup;
    },

    computeAggregates() {
        if (!this.props.list || this.props.list.isGrouped) {
            return {};
        }
        try {
            return super.computeAggregates();
        } catch (error) {
            console.warn("⚠️ computeAggregates error:", error);
            return {};
        }
    },

    getFirstAggregateIndex() {
        if (!this.props.list || this.props.list.isGrouped) {
            return -1;
        }
        try {
            return super.getFirstAggregateIndex();
        } catch (error) {
            console.warn("⚠️ getFirstAggregateIndex error:", error);
            return -1;
        }
    },

    getGroupNameCellColSpan() {
        if (!this.props.list || this.props.list.isGrouped) {
            return this.nbCols || 1;
        }
        try {
            return super.getGroupNameCellColSpan();
        } catch (error) {
            console.warn("⚠️ getGroupNameCellColSpan error:", error);
            return this.nbCols || 1;
        }
    },

    getGroupLevel(group) {
    if (!group) {
        return 0;
    }

    // Safely access groupBy
    const groupBy = this.props.list?.groupBy || [];
    const groupByField = group.groupByField;

    if (!groupByField || !Array.isArray(groupBy)) {
        return 0;
    }

    try {
        return groupBy.indexOf(groupByField.name);
    } catch (error) {
        console.warn("⚠️ getGroupLevel error:", error);
        return 0;
    }
},

getLastAggregateIndex() {
    if (!this.props.list || this.props.list.isGrouped) {
        return -1;
    }
    try {
        return super.getLastAggregateIndex();
    } catch (error) {
        console.warn("⚠️ getLastAggregateIndex error:", error);
        return -1;
    }
},

getAggregateColumns() {
    if (!this.props.list || this.props.list.isGrouped) {
        return [];
    }
    try {
        return super.getAggregateColumns();
    } catch (error) {
        console.warn("⚠️ getAggregateColumns error:", error);
        return [];
    }
},


    get activeActions() {
        // 🧱 SAFEGUARD: this.props might not exist during prototype initialization
        if (!this || !this.props) {
            console.warn("⚠️ [activeActions] this.props not yet available");
            return {}; // Must return an object, not false!
        }

        const { archInfo } = this.props;

        // If archInfo has createGroup enabled, return its activeActions
        if (archInfo?.activeActions?.createGroup) {
            console.log("✨ [activeActions] Using archInfo.activeActions with createGroup");
            return archInfo.activeActions || {};
        } else {
            console.log("📋 [activeActions] Using props.activeActions");
            return this.props.activeActions || {};
        }
    },

    get canCreateGroup() {
        // Add null safety checks
        if (!this || !this.props) {
            console.warn("⚠️ [canCreateGroup] this.props not available");
            return false;
        }

        const { archInfo, list, readonly } = this.props;

        // Check if archInfo exists
        if (!archInfo) {
            console.warn("⚠️ [canCreateGroup] archInfo is undefined");
            return false;
        }

        // Check if list exists
        if (!list) {
            console.warn("⚠️ [canCreateGroup] list is undefined");
            return false;
        }
        console.log('listtttt',list)

        const { activeActions, defaultGroupBy } = archInfo;

        console.log("🔍 [canCreateGroup] Checking conditions:", {
            list,
            readonly,
            hasActiveActions: !!activeActions,
            createGroup: activeActions?.createGroup,
            isGrouped: list.isGrouped,
            hasGroupByField: !!list.groupByField
        });

        // If archInfo has createGroup explicitly enabled, allow it
        if (archInfo?.activeActions?.createGroup) {
            console.log("✅ [canCreateGroup] Enabled via archInfo.activeActions.createGroup");
            return true;
        } else {
            // Otherwise, check standard conditions
            if (!activeActions) {
                console.warn("⚠️ [canCreateGroup] activeActions is undefined");
                return false;
            }



            const result =!readonly &&
            activeActions.createGroup &&
            list.groupByField?.type === "many2one" &&
            list.groupByField?.name === defaultGroupBy?.[0]
            console.log("✅ [canCreateGroup] Standard check result:", result);
            return result;
        }
    },


});

console.log("✅ [PATCH] ListRenderer.activeActions and canCreateGroup overridden safely");