# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RmaPolicyField(models.Model):
    _name = "rma.policy_field"
    _description = "RMA Policy Field"

    name = fields.Char(
        string="Description",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        required=True,
        default=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
