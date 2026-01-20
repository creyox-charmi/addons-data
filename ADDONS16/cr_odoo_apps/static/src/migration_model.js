/** @odoo-module */
import { RelationalModel, DynamicRecordList } from "@web/views/relational_model";

export class MigrationModel extends RelationalModel {
    setup(params, { rpc, action, notification }) {
        this.lastCreatedRecordId = ""; // Track the last created record's ID
        return super.setup(...arguments);
    }
}

export class MigrationDynamicRecordList extends DynamicRecordList {
    async createRecord(params = {}, atFirstPosition = false) {
        const record = await super.createRecord(...arguments);
        // Save the created record ID
        record.model.lastCreatedRecordId = record.id;
        return record;
    }
}

// Attach dynamic record list to the model
MigrationModel.DynamicRecordList = MigrationDynamicRecordList;
