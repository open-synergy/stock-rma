# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import ValidationError


class RmaAddPurchase(models.TransientModel):
    _name = "rma_add_purchase"
    _description = "Wizard to add rma lines"

    @api.model
    def default_get(self, fields):
        res = super(RmaAddPurchase, self).default_get(fields)
        rma_obj = self.env["rma.order"]
        rma_id = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_id:
            return res
        assert active_model == "rma.order", "Bad context propagation"

        rma = rma_obj.browse(rma_id)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
        res["purchase_id"] = False
        res["purchase_line_ids"] = False
        return res

    rma_id = fields.Many2one(
        comodel_name="rma.order",
        string="RMA Order",
        readonly=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=True,
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Order",
    )
    purchase_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="rma_add_purchase_add_line_rel",
        column1="purchase_line_id",
        column2="rma_add_purchase_id",
        readonly=False,
        string="Purcahse Order Lines",
    )

    def _prepare_rma_line_from_po_line(self, line):
        product = line.product_id
        operation = product.supplier_rma_operation_id or False
        if not operation:
            operation = product.categ_id.supplier_rma_operation_id and \
                product.categ_id.rma_operation_id.id or False
        data = {
            "purchase_order_line_id": line.id,
            "product_id": product.id,
            "origin": line.order_id.name,
            "uom_id": line.product_uom.id,
            "operation_id": operation,
            "product_qty": line.product_qty,
            "price_unit": line.price_unit,
            # "price_unit": line.currency_id.compute(
            #     line.price_unit, line.currency_id, round=False),
            "rma_id": self.rma_id.id
        }
        if not operation:
            operation = self.env["rma.operation"].search(
                [("type", "=", self.rma_id.type)], limit=1)
            if not operation:
                raise ValidationError("Please define an operation first")
        if not operation.in_route_id or not operation.out_route_id:
            route = self.env["stock.location.route"].search(
                [("rma_selectable", "=", True)], limit=1)
            if not route:
                raise ValidationError("Please define an rma route")
        data.update(
            {"in_route_id": operation.in_route_id.id or route,
             "out_route_id": operation.out_route_id.id or route,
             "receipt_policy": operation.receipt_policy,
             "location_id": operation.location_id.id or
             self.env.ref("stock.stock_location_stock").id,
             "operation_id": operation.id,
             "refund_policy": operation.refund_policy,
             "delivery_policy": operation.delivery_policy,
             "out_warehouse_id": operation.out_warehouse_id.id,
             "in_warehouse_id": operation.in_warehouse_id.id,
             })
        return data

    @api.model
    def _get_rma_data(self):
        data = {
            "date_rma": fields.Datetime.now(),
            "delivery_address_id": self.purchase_id.partner_id.id,
            "invoice_address_id": self.purchase_id.partner_id.id
        }
        return data

    @api.multi
    def add_lines(self):
        self.ensure_one()
        rma_line_obj = self.env["rma.order.line"]
        rma = self.rma_id
        existing_purchase_lines = rma._get_existing_purchase_lines()
        for line in self.purchase_line_ids:
            # Load a PO line only once
            if line not in existing_purchase_lines:
                data = self._prepare_rma_line_from_po_line(line)
                rma_line_obj.create(data)
        data_rma = self._get_rma_data()
        rma.write(data_rma)
        return {"type": "ir.actions.act_window_close"}
