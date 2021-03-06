# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class RmaOrder(models.Model):
    _inherit = "rma.order"

    @api.depends(
        "rma_line_ids",
        "rma_line_ids.procurement_ids",
    )
    @api.multi
    def _compute_po_count(self):
        for rec in self:
            purchase_list = []
            for line in rec.rma_line_ids:
                for procurement_id in line.procurement_ids:
                    if procurement_id.purchase_id and \
                            procurement_id.purchase_id.id:
                        purchase_list.append(procurement_id.purchase_id.id)
            rec.po_count = len(list(set(purchase_list)))

    @api.one
    def _compute_origin_po_count(self):
        po_list = []
        for rma_line in self.rma_line_ids:
            if rma_line.purchase_order_line_id and \
                    rma_line.purchase_order_line_id.id:
                po_list.append(rma_line.purchase_order_line_id.order_id.id)
        self.origin_po_count = len(list(set(po_list)))

    po_count = fields.Integer(
        compute=_compute_po_count,
        string="# of PO",
        copy=False,
        default=0,
    )
    origin_po_count = fields.Integer(
        compute=_compute_origin_po_count,
        string="# of Origin PO",
        copy=False,
        default=0,
    )

    @api.multi
    def action_view_purchase_order(self):
        action = self.env.ref("purchase.purchase_rfq")
        result = action.read()[0]
        order_ids = []
        for line in self.rma_line_ids:
            for procurement_id in line.procurement_ids:
                order_ids.append(procurement_id.purchase_id.id)
        result["domain"] = [("id", "in", order_ids)]
        return result

    @api.multi
    def action_view_origin_purchase_order(self):
        action = self.env.ref("purchase.purchase_rfq")
        result = action.read()[0]
        order_ids = []
        for rma_line in self.rma_line_ids:
            if rma_line.purchase_order_line_id and \
                    rma_line.purchase_order_line_id.id:
                order_ids.append(rma_line.purchase_order_line_id.order_id.id)
        result["domain"] = [("id", "in", order_ids)]
        return result

    @api.multi
    def _get_existing_purchase_lines(self):
        self.ensure_one()
        existing_purchase_lines = self.env["purchase.order.line"]
        for rma_line in self.rma_line_ids:
            if rma_line.purchase_order_line_id:
                existing_purchase_lines += rma_line.purchase_order_line_id
        return existing_purchase_lines
