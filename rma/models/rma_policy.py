# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class RmaPolicy(models.Model):
    _name = "rma.policy"
    _description = "RMA Policy"

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
        required=False,
    )
    rma_type = fields.Selection(
        selection=[
            ("customer", "Customer"),
            ("supplier", "Supplier"),
            ("both", "Both"),
        ],
        string="Applicable on RMA Type",
        required=True,
        default="customer",
    )
    policy_rule_ids = fields.One2many(
        string="Policy Rules",
        comodel_name="rma.policy_rule",
        inverse_name="rma_policy_id",
        )
    receipt_policy_ok = fields.Boolean(
        string="Available on Receipt Policy"
        )
    delivery_policy_ok = fields.Boolean(
        string="Available on Delivery Policy"
        )
    rma_supplier_policy_ok = fields.Boolean(
        string="Available on RMA to Supplier Policy"
        )

    @api.multi
    def _compute_quantity(self, rma_line_id):
        self.ensure_one()
        qty = 0.0
        for rule in self.policy_rule_ids:
            if rule.operator == "+":
                qty += getattr(rma_line_id, rule.policy_field_id.code)
            elif rule.operator == "-":
                qty -= getattr(rma_line_id, rule.policy_field_id.code)
        return qty
