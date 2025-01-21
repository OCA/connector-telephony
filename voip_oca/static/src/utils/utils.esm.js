/** @odoo-module **/
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

import {_t} from "@web/core/l10n/translation";

export function normalize(str) {
    return str
        .toLowerCase()
        .replaceAll(/\p{Diacritic}/gu, "")
        .normalize("NFD");
}

export function matchString(targetString, substring) {
    if (!targetString) {
        return false;
    }
    return normalize(targetString).includes(normalize(substring));
}

export function durationStr(duration) {
    if (!duration) {
        return "";
    }
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    if (!minutes) {
        switch (seconds) {
            case 0:
                return _t("less than a second");
            case 1:
                return _t("1 second");
            default:
                return _t("%(seconds)s seconds", {seconds});
        }
    }
    if (!seconds) {
        switch (minutes) {
            case 1:
                return _t("1 minute");
            case 2:
                return _t("2 minutes");
            default:
                return _t("%(minutes)s minutes", {minutes});
        }
    }
    return _t("%(minutes)s min %(seconds)s sec", {minutes, seconds});
}
