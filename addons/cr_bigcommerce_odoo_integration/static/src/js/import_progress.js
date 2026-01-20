/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ImportProgressDialog extends Component {
    static template = "bigcommerce.ImportProgressDialog";
    static props = {
        close: Function,
        storeId: Number,
        importType: String,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            status: 'true',
            total_processed: 0,
            total_expected: 0,
            created: 0,
            updated: 0,
            elapsed_time: '0m 0s',
            error_message: '',
            progress_percentage: 0,
        });

        this.intervalId = null;

        onMounted(() => {
            this.fetchProgress();
            this.intervalId = setInterval(() => this.fetchProgress(), 2000);
        });

        onWillUnmount(() => {
            if (this.intervalId) {
                clearInterval(this.intervalId);
            }
        });
    }

    async fetchProgress() {
        try {
            const result = await this.orm.call(
                "bigcommerce.store",
                "get_import_progress",
                [this.props.storeId],
                { import_type: this.props.importType }
            );

            this.state.status = result.status;
            this.state.total_processed = result.total_processed;
            this.state.total_expected = result.total_expected || 0;
            this.state.created = result.created;
            this.state.updated = result.updated;
            this.state.elapsed_time = result.elapsed_time;
            this.state.error_message = result.error_message;

            if (this.state.total_expected > 0) {
                this.state.progress_percentage = Math.min(99,
                    (this.state.total_processed / this.state.total_expected) * 100
                );
            }

            if (result.status === 'completed') {
                this.state.progress_percentage = 100;
                clearInterval(this.intervalId);
            }
        } catch (error) {
            console.error("Failed to fetch progress:", error);
        }
    }
}

// THIS IS THE CORRECT WAY FOR ODOO 18
class ImportProgressAction extends Component {
    static template = "bigcommerce.ImportProgressAction";
    static components = { ImportProgressDialog };
    static props = ["*"];

    setup() {
        this.dialogService = useService("dialog");

        onMounted(() => {
            this.openDialog();
        });
    }

    openDialog() {
        const typeMap = {
            'customer': 'Customer',
            'address': 'Address',
            'product': 'Product',
            'order': 'Order'
        };

        this.dialogService.add(ImportProgressDialog, {
            storeId: this.props.action.params.store_id,
            importType: this.props.action.params.import_type,
        }, {
            title: `${typeMap[this.props.action.params.import_type]} Import Progress`,
            size: 'lg',
        });
    }
}

registry.category("actions").add("bigcommerce_import_progress", ImportProgressAction);