# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class RmaMakePicking(models.TransientModel):
    _inherit = "rma_make_picking.wizard"

    @api.returns("rma.order.line")
    def _prepare_item(self, line):
        res = super(RmaMakePicking, self)._prepare_item(line)
        res["sale_line_id"] = line.sale_line_id.id
        return res


class RmaMakePickingItem(models.TransientModel):
    _inherit = "rma_make_picking.wizard.item"

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Line",
    )
