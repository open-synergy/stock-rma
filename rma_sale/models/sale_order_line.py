# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rma_line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA",
        ondelete="restrict",
    )

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        vals.update({
            "rma_line_id": self.rma_line_id.id
        })
        return vals
