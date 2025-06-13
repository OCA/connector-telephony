/* @odoo-module */

import {Record} from "@mail/core/common/record";
import {deserializeDateTime} from "@web/core/l10n/dates";
import {durationStr} from "../../utils/utils.esm";

/**
 * @typedef Data
 * @property {[number, string]} partner_id
 * @property {[number, string]} user_id
 * @property {[number, string]} create_uid
 * @property {[number, string]} write_uid
 * @property {String} phone_number
 * @property {'incoming'|'outgoing'} type_call
 * @property {'aborted', 'calling', 'missed', 'ongoing', 'rejected', 'terminated'} state
 * @property {String} activity_name
 * @property {String} end_date
 * @property {String} start_date
 * @property {String} create_date
 * @property {String} write_date
 */

export class Call extends Record {
    static id = "id";
    /** @type {Object.<number, Call>} */
    static records = {};
    /**
     * @param {Data} data
     * @returns {Call}
     * */
    static get(data) {
        return super.get(data);
    }
    /**
     * @returns {Call|Call[]}
     */
    static insert() {
        return super.insert(...arguments);
    }
    /**
     * Deserialize the data and update the record.
     * @param {Data} data
     */
    update(data) {
        super.update(...arguments);
        if (data.createDate) {
            this.createDate = deserializeDateTime(data.createDate);
        }
        if (data.startDate) {
            this.startDate = deserializeDateTime(data.startDate);
        }
        if (data.endDate) {
            this.endDate = deserializeDateTime(data.endDate);
        }
    }
    /**
     * Date of the call to show
     * @returns {Date}
     */
    get date() {
        if (this.startDate) {
            return this.startDate;
        }
        return this.createDate;
    }
    /**
     * Date of the call to show
     * @returns {String}
     */
    get dateStr() {
        return this.date.toLocaleString(luxon.DateTime.DATETIME_SHORT);
    }
    get iconTypeCall() {
        if (this.typeCall === "incoming") {
            return "fa fa-arrow-down";
        }
        return "fa fa-arrow-up";
    }
    /**
     * Duration of the call in seconds.
     * @returns {Number}
     */
    get duration() {
        if (!this.startDate || !this.endDate) {
            return 0;
        }
        return (this.endDate - this.startDate) / 1000;
    }
    /**
     * String translation of the duration of the call.
     * @returns {String}
     */
    get durationStr() {
        return durationStr(this.duration);
    }
}

Call.register();
