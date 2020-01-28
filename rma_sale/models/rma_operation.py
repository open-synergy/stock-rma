# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class RmaOperation(models.Model):
    _inherit = "rma.operation"

    @api.model
    def _default_sale_policy(self):
        try:
            result = self.env.ref("rma.rma_policy_no")
        except ValueError:
            result = self.env["rma.policy"]._create_default_policy()
        return result

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
