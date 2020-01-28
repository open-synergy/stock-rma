# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RmaPolicy(models.Model):
    _inherit = "rma.policy"

    sale_policy_ok = fields.Boolean(
        string="Available on Sale Policy"
    )
