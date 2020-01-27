# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from datetime import datetime


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

    @api.model
    def _create_default_policy(self):
        res = {
            "name": "Not Needed",
            "rma_type": "both",
        }
        default_policy = self.env["rma.policy"].create(res)
        self.env["ir.model.data"].sudo().create({
            "name": "rma_policy_no",
            "model": "rma.policy",
            "module": "rma",
            "res_id": default_policy.id,
            "date_init": datetime.now(),
            "date_update": datetime.now(),
        })
        return default_policy
