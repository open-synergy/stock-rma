# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class RmaAddStockMove(models.TransientModel):
    _name = "rma_add_stock_move"
    _description = "Wizard to add rma lines from pickings"

    @api.model
    def default_get(self, fields):
        res = super(RmaAddStockMove, self).default_get(fields)
        rma_obj = self.env["rma.order"]
        rma_id = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_id:
            return res
        assert active_model == "rma.order", "Bad context propagation"

        rma = rma_obj.browse(rma_id)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
        res["picking_id"] = False
        res["move_ids"] = False
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
    move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Stock Moves",
        domain="[('state', '=', 'done')]",
    )

    @api.model
    def _prepare_rma_line_from_stock_move(self, sm, lot=False):
        operation = sm.product_id.product_tmpl_id._get_rma_operation(
            self.rma_id.type)
        data = {
            "reference_move_id": sm.id,
            "product_id": sm.product_id.id,
            "lot_id": lot and lot.id or False,
            "name": sm.product_id.name_template,
            "origin": sm.picking_id.name,
            "uom_id": sm.product_uom.id,
            "operation_id": operation.id,
            "product_qty": sm.product_uom_qty,
            "delivery_address_id": sm.picking_id.partner_id.id,
            "rma_id": self.rma_id.id
        }

        if not operation:
            raise ValidationError(_("Please define an operation first"))

        if not operation.in_route_id or not operation.out_route_id:
            route = self.env["stock.location.route"].search(
                [("rma_selectable", "=", True)], limit=1)
            if not route:
                raise ValidationError("Please define an rma route")
        data.update(
            {"in_route_id": operation.in_route_id.id,
             "out_route_id": operation.out_route_id.id,
             "receipt_policy": operation.receipt_policy,
             "operation_id": operation.id,
             "refund_policy": operation.refund_policy,
             "delivery_policy": operation.delivery_policy
             })
        if operation.in_warehouse_id:
            data["in_warehouse_id"] = operation.in_warehouse_id.id
        if operation.out_warehouse_id:
            data["out_warehouse_id"] = operation.out_warehouse_id.id
        if operation.location_id:
            data["location_id"] = operation.location_id.id
        return data

    @api.model
    def _get_existing_stock_moves(self):
        existing_move_lines = []
        for rma_line in self.rma_id.rma_line_ids:
            existing_move_lines.append(rma_line.reference_move_id)
        return existing_move_lines

    @api.multi
    def add_lines(self):
        rma_line_obj = self.env["rma.order.line"]
        existing_stock_moves = self._get_existing_stock_moves()
        for sm in self.move_ids:
            if sm not in existing_stock_moves:
                if sm.lot_ids:
                    for lot in sm.lot_ids:
                        data = self._prepare_rma_line_from_stock_move(sm,
                                                                      lot=lot)
                        rma_line_obj.with_context(
                            default_rma_id=self.rma_id.id).create(data)
                else:
                    data = self._prepare_rma_line_from_stock_move(
                        sm, lot=False)
                    rma_line_obj.with_context(
                        default_rma_id=self.rma_id.id).create(data)
        return {"type": "ir.actions.act_window_close"}
