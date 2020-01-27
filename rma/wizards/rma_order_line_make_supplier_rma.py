# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.addons.decimal_precision as dp
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class RmaLineMakeSupplierRma(models.TransientModel):
    _name = "rma.order.line.make.supplier.rma"
    _description = "RMA Line Make Supplier RMA"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=False,
        domain=[
            ("supplier", "=", True),
        ],
    )
    item_ids = fields.One2many(
        comodel_name="rma.order.line.make.supplier.rma.item",
        inverse_name="wiz_id",
        string="Items",
    )
    supplier_rma_id = fields.Many2one(
        comodel_name="rma.order",
        string="Supplier RMA Order",
        required=False,
        domain=[
            ("state", "=", "draft"),
        ],
    )

    @api.model
    def _prepare_item(self, line):
        return {
            "line_id": line.id,
            "product_id": line.product_id.id,
            "name": line.name,
            "product_qty": line.qty_to_supplier_rma,
            "uom_id": line.uom_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super(RmaLineMakeSupplierRma, self).default_get(
            fields)
        rma_line_obj = self.env["rma.order.line"]
        rma_line_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]

        if not rma_line_ids:
            return res
        assert active_model == "rma.order.line", "Bad context propagation"

        items = []
        lines = rma_line_obj.browse(rma_line_ids)
        for line in lines:
            items.append([0, 0, self._prepare_item(line)])
        suppliers = lines.mapped("supplier_address_id")
        if len(suppliers) == 1:
            res["partner_id"] = suppliers.id
        else:
            raise UserError(
                _("Only RMA lines from the same supplier address can be "
                  "processed at the same time"))
        res["item_ids"] = items
        return res

    @api.multi
    def _prepare_supplier_rma(self):
        if not self.partner_id:
            raise UserError(
                _("Enter a supplier."))
        return {
            "partner_id": self.partner_id.id,
            "delivery_address_id": self.partner_id.id,
            "type": "supplier",
            "company_id": self.env.user.company_id.id,
        }

    @api.multi
    def _get_supplier_rma(self):
        self.ensure_one()
        rma = False
        if self.supplier_rma_id:
            rma = self.supplier_rma_id
        if not rma:
            rma_data = self._prepare_supplier_rma()
            rma = self.env["rma.order"].create(rma_data)
        return rma

    @api.multi
    def make_supplier_rma(self):
        self.ensure_one()
        res = []
        rma = self._get_supplier_rma()

        for item in self.item_ids:
            item._create_supplier_rma_line(rma)
        res.append(rma.id)

        return {
            "domain": "[('id','in', [" + ",".join(map(str, res)) + "])]",
            "name": _("Supplier RMA"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "rma.order",
            "view_id": False,
            "context": {"supplier": 1},
            "type": "ir.actions.act_window"
        }


class RmaLineMakeRmaOrderItem(models.TransientModel):
    _name = "rma.order.line.make.supplier.rma.item"
    _description = "RMA Line Make Supplier RMA Item"

    wiz_id = fields.Many2one(
        comodel_name="rma.order.line.make.supplier.rma",
        string="Wizard",
        required=False,
        ondelete="cascade",
        readonly=True,
    )
    line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA Line",
        required=True,
    )
    rma_id = fields.Many2one(
        comodel_name="rma.order",
        related="line_id.rma_id",
        string="RMA Order",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_id.product_id",
        readony=True,
    )
    name = fields.Char(
        related="line_id.name",
        readonly=True,
    )
    uom_id = fields.Many2one(
        comodel_name="product.uom",
        string="UoM",
        readonly=True,
    )
    product_qty = fields.Float(
        string="Quantity to RMA Supplier",
        digits=dp.get_precision("Product UoS"),
    )

    @api.multi
    def _check_qty(self):
        self.ensure_one()
        if self.product_qty <= 0.0:
            raise UserError(
                _("Enter a positive quantity."))

    @api.multi
    def _create_supplier_rma_line(self, rma):
        rma_line_data = self._prepare_supplier_rma_line(rma)
        res = self.env["rma.order.line"].create(rma_line_data)
        return res

    @api.multi
    def _prepare_supplier_rma_line(self, rma):
        self.ensure_one()
        operation = self.env["rma.operation"].search(
            [("type", "=", "supplier")], limit=1)
        return {
            "origin": self.line_id.rma_id.name,
            "delivery_address_id":
                self.line_id.delivery_address_id.id,
            "product_id": self.line_id.product_id.id,
            "customer_rma_id": self.line_id.id,
            "product_qty": self.product_qty,
            "uom_id": self.uom_id.id,
            "rma_id": rma.id,
            "operation_id": operation.id,
            "receipt_policy_id": operation.receipt_policy_id.id,
            "delivery_policy_id": operation.delivery_policy_id.id,
            "in_warehouse_id": operation.in_warehouse_id.id,
            "out_warehouse_id": operation.out_warehouse_id.id,
            "location_id": self.line_id.location_id.id,
            "supplier_to_customer": operation.supplier_to_customer,
            "in_route_id": operation.in_route_id.id,
            "out_route_id": operation.out_route_id.id,
        }
