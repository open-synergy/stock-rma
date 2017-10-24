# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class QualityInspection(models.Model):
    _inherit = "qc.inspection"

    @api.multi
    def _create_rma_line_from_inspection(self, rma, operation=False):
        self.ensure_one()
        po_line = self.env["rma.order.line"].create(
            self._prepare_rma_line_from_inspection(rma, operation))
        return po_line

    @api.multi
    def _prepare_rma_line_from_inspection(self, rma, operation=False):
        self.ensure_one()
        if not operation:
            operation = self.product_id.product_tmpl_id._get_rma_operation(
                rma.type)

        if not operation:
            raise UserError(_("Please define an operation first"))

        if not operation.in_route_id or not operation.out_route_id:
            route = self.env["stock.location.route"].search(
                [("rma_selectable", "=", True)], limit=1)
            if not route:
                raise UserError(_("Please define an rma route"))
        cur = self.env.user.company_id.currency_id
        data = {
            "quality_inspection_id": self.id,
            "product_id": self.product.id,
            "origin": self.name,
            "uom_id": self.product.uom_id.id,
            "operation_id": operation.id,
            "product_qty": self.qty,
            "lot_id": self.lot and self.lot.id or False,
            # TODO
            "price_unit": 0.0,
            "currency_id": cur.id,
            "rma_id": rma.id,
            "in_route_id": operation.in_route_id.id or route.id,
            "out_route_id": operation.out_route_id.id or route.id,
            "receipt_policy": operation.receipt_policy,
            "location_id": operation.location_id.id or
            self.env.ref("stock.stock_location_stock").id,
            "delivery_policy": operation.delivery_policy,
            "out_warehouse_id": operation.out_warehouse_id.id,
            "in_warehouse_id": operation.in_warehouse_id.id,
        }
        return data
