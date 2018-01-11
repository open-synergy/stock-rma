# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


drop_columns = [
    ("rma_order_line", "repair_type"),
    ("rma_operation", "repair_type"),
]


def map_rma_operation(env):
    openupgrade.map_values(
        env.cr,
        "repair_type",
        "repair_policy_id",
        [
            ("no", env.ref("rma.rma_policy_no").id),
            ("ordered",
                env.ref("rma_repair.rma_policy_ordered_repaired").id),
            ("received",
                env.ref("rma_repair.rma_policy_received_repaired").id),
        ],
        table="rma_operation",
        write="sql",
    )


def map_rma_order_line(env):
    openupgrade.map_values(
        env.cr,
        "repair_type",
        "repair_policy_id",
        [
            ("no", env.ref("rma.rma_policy_no").id),
            ("ordered",
                env.ref("rma_repair.rma_policy_ordered_repaired").id),
            ("received",
                env.ref("rma_repair.rma_policy_received_repaired").id),
        ],
        table="rma_order_line",
        write="sql",
    )


@openupgrade.migrate()
def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        map_rma_operation(env)
        map_rma_order_line(env)
    openupgrade.drop_columns(cr, drop_columns)
