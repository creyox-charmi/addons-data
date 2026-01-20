/** @odoo-module */

import { listView } from "@web/views/list/list_view";
import { CustomMigrationController } from "./migration_controller";
import { MigrationModel } from "./migration_model";
import { registry } from "@web/core/registry";

export const CrMigrationListView = {
    ...listView,
    Controller: CustomMigrationController,
    Model : MigrationModel,
    buttonTemplate: 'Migration.Buttons',
};

registry.category("views").add('cr_migration_button', CrMigrationListView);


