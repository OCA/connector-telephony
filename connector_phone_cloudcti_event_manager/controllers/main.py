import json
import logging
import re
from datetime import datetime

import phonenumbers
import pytz

from odoo import http
from odoo.http import Response, request

_logger = logging.getLogger(__name__)


class CloudCTIVOIP(http.Controller):
    def map_state(self, instate, currentstate=False):
        outstate = "on_hold"
        if instate == "ringing":
            outstate = "offering"
        elif instate == "answered":
            outstate = "connected"
        elif instate == "ended":
            if currentstate == "offering":
                outstate = "missed"
            elif currentstate == "connected":
                outstate = "completed"
        else:
            outstate = "on_hold"
        return outstate

    def create_cdr_record(self, user, payload):
        startdate = False
        if payload.get("starttime"):
            startdate = self.convert_into_correct_timezone(
                payload.get("starttime"), user
            )
        vals = {
            "guid": payload.get("callid"),
            "inbound_flag": payload.get("direction").lower(),
            "called_id": payload.get("calledid"),
            "called_id_name": user.name,
            "caller_id": payload.get("callerid"),
            "call_start_time": startdate,
            "state": self.map_state(payload.get("state")),
            "user_id": user.id,
            "partner_ids": payload.get("partner_ids"),
        }
        return request.env["phone.cdr"].sudo().create(vals)

    def convert_into_correct_timezone(self, record_date, user):
        # CloudCTI provides date in UTC, so no conversion needed.
        return re.sub(r"[TtzZ]", " ", record_date)
        record_date = datetime.strptime(record_date, "%Y-%m-%d %H:%M:%S")
        timezone = request.env.context.get("tz", False) or user.partner_id.tz
        return_date = None
        if timezone:
            src_tz = pytz.timezone("UTC")
            dst_tz = pytz.timezone(timezone)
            return_date = dst_tz.localize(record_date).astimezone(src_tz)
        return return_date

    @http.route("/cloudCTI/statusChange", type="json", auth="public")
    def cloudcti_status_change(self, *args, **kw):
        # check for data
        if kw:
            guid = kw.get("CallId")
            callednumber = kw.get("CalledNumber")
            callernumber = kw.get("CallerNumber")
            direction = kw.get("Direction")
            state = kw.get("State")
            starttime = kw.get("StartTime") or False
            endtime = kw.get("EndTime") or False
            duration = kw.get("CallDuration") or 0.0
            _logger.info("Webhook ---- %s", kw)
        else:
            return Response(json.dumps({}))
        phone = other = False
        if direction == "inbound":
            phone = callednumber
            other = callernumber
            create = True if state == "ringing" else False
            check = True if state == "answered" else False
        elif direction == "outbound":
            phone = callernumber
            other = callednumber
            create = True if state == "ringing" else False
            check = True if state == "answered" else False
        phone = phonenumbers.format_number(
            phonenumbers.parse(phone, "US"), phonenumbers.PhoneNumberFormat.NATIONAL
        )
        other = phonenumbers.format_number(
            phonenumbers.parse(other, "US"), phonenumbers.PhoneNumberFormat.NATIONAL
        )
        user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
        if not user:
            user = request.env["res.users"].sudo().browse(1)
        if not user:
            return Response(json.dumps({"message": "User Not found.", "status": 404}))
        else:
            partner = (
                request.env["phone.common"].sudo().get_record_from_phone_number(other)
            )
            if create:
                payload = {
                    "callid": guid,
                    "callerid": phone if direction == "outbound" else other,
                    "calledid": phone if direction == "inbound" else other,
                    "direction": direction,
                    "state": state,
                    "starttime": starttime,
                    "partner_ids": [(6, 0, partner.ids)],
                }
                _logger.info("CDR Payload ---- %s", payload)
                cdr = self.create_cdr_record(user, payload)
                # if it is not external call, and incoming, only cdr is needed, exit here
                if user.id > 1 and direction.lower() == "inbound" and cdr:
                    return (
                        request.env["phone.common"]
                        .sudo()
                        .incall_notify_by_login(
                            other,
                            [user.login],
                            calltype="Incoming Call",
                        )
                    )
                else:
                    return Response(json.dumps({}))
            else:
                cdr = (
                    request.env["phone.cdr"]
                    .sudo()
                    .search([("guid", "=", guid)], limit=1)
                )
                # need to check and create record
                if check and not cdr:
                    payload = {
                        "callid": guid,
                        "callerid": phone if direction == "outbound" else other,
                        "calledid": phone if direction == "inbound" else other,
                        "direction": direction,
                        "state": state,
                        "starttime": starttime,
                        "partner_ids": [(6, 0, partner.ids)],
                    }
                    _logger.info("CDR Payload ---- %s", payload)
                    cdr = self.create_cdr_record(user, payload)

                enddate = False
                if endtime:
                    enddate = self.convert_into_correct_timezone(endtime, user)
                payload = {
                    "state": self.map_state(state, cdr.state),
                    "call_end_time": enddate,
                    "call_duration": duration,
                }
                cdr.sudo().write(payload)
        return Response(json.dumps({}))
