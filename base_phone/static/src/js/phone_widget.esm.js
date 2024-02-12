/** @odoo-module **/

/* Base phone module for Odoo
   Copyright (C) 2013-2018 Akretion France
   @author: Alexis de Lattre <alexis.delattre@akretion.com>
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {_t} from "@web/core/l10n/translation";
import {
    PhoneField,
    formPhoneField,
    phoneField,
} from "@web/views/fields/phone/phone_field";
import {patch} from "@web/core/utils/patch";
import {Component} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class Dial extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }
    get phoneHref() {
        return "tel:" + this.props.record.data[this.props.name].replace(/\s+/g, "");
    }
    async onClick() {
        await this.props.record.save();
        var phone_num = this.props.record.data[this.props.name];
        this.env.services.notification.add(_t('Click2dial to "%s"', phone_num), {
            type: "info",
        });
        var params = {
            phone_number: phone_num,
            click2dial_model: this.props.record.resModel,
            click2dial_id: this.props.record.resId,
        };
        const result = await this.orm.call(
            "phone.common",
            "click2dial",
            [phone_num],
            {}
        );
        if (result === false) {
            this.env.services.notification.add(_t("Click2dial failed"), {
                type: "warning",
            });
        } else if (typeof result === "object") {
            this.env.services.notification.add(
                (_t("Number dialed: %s"), result.dialed_number),
                {title: _t("Click2dial successfull"), type: "success"}
            );
            if (result.action_model) {
                this.action.doAction({
                    type: "ir.actions.act_window",
                    name: result.action_name,
                    res_model: result.action_model,
                    views: [[false, "form"]],
                    target: "new",
                    context: params,
                });
            }
        }
    }
}
Dial.template = "base_phone.Dial";
Dial.props = ["*"];

patch(PhoneField, {
    components: {
        ...PhoneField.components,
        Dial,
    },
    defaultProps: {
        ...PhoneField.defaultProps,
        enableButton: true,
    },
    props: {
        ...PhoneField.props,
        enableButton: {type: Boolean, optional: true},
    },
});

const patchDescr = () => ({
    extractProps({options}) {
        const props = super.extractProps(...arguments);
        props.enableButton = options.enable_sms;
        return props;
    },
});

patch(phoneField, patchDescr());
patch(formPhoneField, patchDescr());
