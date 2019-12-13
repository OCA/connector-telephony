# coding: utf-8
# Copyright 2019 Opener B.V. (<https://opener.amsterdam>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """ Set the sales team from the user settings instead of applying the
    global default to all records.

    Because this is a newly installed 'glue' module, the migration needs to run
    when `version` (the previously installed version from which we are
    upgrading from) is not set. """
    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'crm_phonecall'")
    if not cr.fetchone():  # New installation
        return

    cr.execute(
        "ALTER TABLE crm_phonecall ADD COLUMN IF NOT EXISTS team_id INT")
    cr.execute(
        """UPDATE crm_phonecall cp SET team_id = ru.sale_team_id
        FROM res_users ru WHERE cp.create_uid = ru.id
        AND ru.sale_team_id IS NOT NULL""")
    cr.execute(
        """SELECT res_id FROM ir_model_data
        WHERE module = 'sales_team'
            AND name = 'team_sales_department'""")
    row = cr.fetchone()
    if row:
        cr.execute(
            """UPDATE crm_phonecall cp SET team_id = %s
            WHERE team_id IS NULL""", (row[0],))
