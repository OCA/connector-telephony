-- Copyright (C) 2016 Trever L. Adams
-- based on code and ideas by Craig Gowing <craig.gowing@credativ.co.uk>
-- & Alexis de Lattre <alexis.delattre@akretion.com>
-- License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

-- This module assumes calls start at creation not answer.
-- It works on incoming and outgoing calls.
-- See code for the line to uncomment to change this.

-- Add the following to the appropriate places in your dialplan
-- Outbound (default dialplan, extension to extension, and anything out via gateway or via FXO:
-- <action application="set" data="api_hangup_hook=lua freeswitch_logcall.lua"/>
-- Inbound (public dialplan):
-- <action application="export" data="odoo_type=inbound"/>
-- <action application="export" data="nolocal:api_hangup_hook=lua freeswitch_logcall.lua"/>

require("xmlrpc.http")

function string.starts(String,Start)
   return string.sub(String,1,string.len(Start))==Start
end

function GetFileName(url)
  if url == nil then
    return ""
  end
  return url:match("^.+/(.+)$")
end

function getTransferTarget(app_data)
  if app_data == nil then
    return ""
  end
  app_data = app_data:gsub("-.?leg%s*", "")
  app_data = app_data:sub(1, string.find(app_data, " "), -2)
  return app_data
end

-- Change these to meet your installation
local port=8069;
local server="localhost";
options_database = "odoo-test"
options_userid = 1
options_password = "testtesttest"

-- Best not change anything below
local protocol="https"
server_string = protocol .. "://" .. server .. ":" .. port .. "/xmlrpc/2/object"

function odoo_report_call(odoo_type, odoo_src, odoo_dst, odoo_duration, odoo_start, odoo_filename, odoo_uniqueid, odoo_description)
  local ok, res = xmlrpc.http.call(server_string, 'execute', options_database, options_userid, options_password,
                  'phone.common', 'log_call_and_recording', odoo_type, odoo_src, odoo_dst, odoo_duration, odoo_start,
                  odoo_filename, odoo_uniqueid, odoo_description)
  assert(ok, string.format("XML-RPC call failed on client: %s", tostring(res)))
end

  odoo_hangupcause = env:getHeader("variable_hangup_cause")
  if odoo_hangupcause == "LOSE_RACE" or odoo_hangupcause == "ORIGINATOR_CANCEL" then
    return
  end

  odoo_type = env:getHeader("odoo_type")
  if odoo_type == 'inbound' then
    odoo_type = 'incoming'
  else
    odoo_type = 'outgoing'
  end
  if env:getHeader("Caller-RDNIS") then
    redirected = true
  end
  name = env:getHeader("origination_caller_id_name")
  if name == "Odoo Connector" then
    odoo_type = 'outgoing'
  end
  odoo_connector = env:getHeader("odoo_connector")
  if odoo_connector then
    odoo_src = env:getHeader("dialed_user")
  else
    odoo_src = env:getHeader("Caller-Caller-ID-Number")
  end
  odoo_dst = env:getHeader("Caller-Destination-Number")
  odoo_dst2 = env:getHeader("Other-Leg-Destination-Number")
  if odoo_dst2 then
    if string.len(odoo_dst) < string.len(odoo_dst2) then
      odoo_dst = odoo_dst2
    end
  end
  if redirected and odoo_type == "outgoing" and odoo_connector == nil then
    odoo_src, odoo_dst = odoo_dst, odoo_src
  end
  odoo_filename = env:getHeader("variable_rec_file")
  odoo_uniqueid = env:getHeader("variable_uuid")

  if odoo_filename == nil then
    odoo_filename = ""
  else
    odoo_filename = GetFileName(odoo_filename)
  end
  if odoo_hangupcause == nil then
    odoo_hangupcause = ""
  end
  app_name = env:getHeader("variable_last_app")
  app_data = getTransferTarget(env:getHeader("variable_last_arg"))
  if app_name == "transfer" then
    odoo_hangupcause = "[" .. odoo_hangupcause .. " / TRANSFERRED TO: " .. app_data .. "]"
  else
    odoo_hangupcause = "[" .. odoo_hangupcause .. "]"
  end

  if redirected == true then
    odoo_start = tonumber(env:getHeader("bridge_epoch"))
  else
    odoo_start = tonumber(env:getHeader("start_epoch"))
--    odoo_start = tonumber(env:getHeader("answer_epoch"))
  end
  local end_epoch = tonumber(env:getHeader("end_epoch"))
  if odoo_start ~= nil and end_epoch ~= nil then
    odoo_duration = tonumber(end_epoch) - tonumber(odoo_start)
  end
  if string.starts(odoo_dst, "u:") then
    presence_id = env:getHeader("presence_id")
    odoo_dst = presence_id:sub(1, string.find(presence_id, "@") - 1)
  end
  if string.starts(odoo_src, "u:") then
    presence_id = env:getHeader("presence_id")
    odoo_src = presence_id:sub(1, string.find(presence_id, "@") - 1)
  end

odoo_report_call(odoo_type, odoo_src, odoo_dst, tostring(odoo_duration), tostring(odoo_start), odoo_filename, odoo_uniqueid, odoo_hangupcause)
