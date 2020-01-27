# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class RmaPolicyRule(models.Model):
    _name = "rma.policy_rule"
    _description = "RMA Policy Rule"
    _order = "sequence, id"

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
    )
    operator = fields.Selection(
        string="Operator",
        selection=[
            ("-", "-"),
            ("+", "+"),
        ],
        required=True,
        default="+",
    )
    policy_field_id = fields.Many2one(
        string="Field",
        comodel_name="rma.policy_field",
        required=True,
    )
    rma_policy_id = fields.Many2one(
        string="RMA Policy",
        comodel_name="rma.policy",
    )
