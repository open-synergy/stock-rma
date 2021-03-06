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
        res["purchase_order_line_id"] = line.purchase_order_line_id.id
        return res

    @api.model
    def _get_action(self, pickings, procurements):
        po_list = []
        for procurement in procurements:
            if procurement.purchase_id and \
                    procurement.purchase_id.id:
                po_list.append(procurement.purchase_id.id)
        if len(po_list):
            action = self.env.ref("purchase.purchase_rfq")
            result = action.read()[0]
            result["domain"] = [("id", "in", po_list)]
            return result
        else:
            action = super(RmaMakePicking, self)._get_action(pickings,
                                                             procurements)
            return action


class RmaMakePickingItem(models.TransientModel):
    _inherit = "rma_make_picking.wizard.item"

    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Purchase Line",
    )
