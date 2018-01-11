# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models, api


class RmaOperation(models.Model):
    _inherit = "rma.operation"

    @api.model
    def _default_sale_policy(self):
        return self.env.ref("rma.rma_policy_no") or False

    sale_policy_id = fields.Many2one(
        string="Sale Policy",
        comodel_name="rma.policy",
        domain=[
            ("rma_type", "=", "both"),
            ("sale_policy_ok", "=", True),
        ],
        required=True,
        default=lambda self: self._default_sale_policy(),
    )
