# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class RmaOperation(models.Model):
    _inherit = "rma.operation"

    refund_policy = fields.Selection(
        selection=[
            ("no", "No refund"),
            ("ordered", "Based on Ordered Quantities"),
            ("received", "Based on Received Quantities"),
            ("unreplaceable", "Based on Unreplaceable Quantities"),
        ],
        string="Refund Policy",
        default="no",
    )
