# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from openerp import fields, models, api


class RmaOperation(models.Model):
    _inherit = 'rma.operation'

    @api.model
    def _default_repair_policy(self):
        try:
            result = self.env.ref("rma.rma_policy_no")
        except ValueError:
            result = self.env["rma.policy"]._create_default_policy()
        return result

    repair_policy_id = fields.Many2one(
        string="Repair Policy",
        comodel_name="rma.policy",
        domain=[
            ("rma_type", "in", ["both", "customer"]),
            ("repair_policy_ok", "=", True),
        ],
        required=True,
        default=lambda self: self._default_repair_policy(),
    )
