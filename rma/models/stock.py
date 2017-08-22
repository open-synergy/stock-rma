# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_assign(self):
        """When you try to bring back a product from a customer location,
        it may happen that there is no quants available to perform the
        picking."""
        res = super(StockPicking, self).action_assign()
        for picking in self:
            for move in picking.move_lines:
                if (move.rma_line_id and move.state == "confirmed" and
                        move.location_id.usage == "customer"):
                    move.force_assign()
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    rma_line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA line",
        ondelete="restrict",
    )

    @api.model
    def create(self, vals):
        if vals.get("procurement_id"):
            procurement = self.env["procurement.order"].browse(
                vals["procurement_id"])
            if procurement.rma_line_id:
                vals["rma_line_id"] = procurement.rma_line_id.id
        return super(StockMove, self).create(vals)

    @api.multi
    def _create_rma_line(self, rma):
        self.ensure_one()
        obj_line = self.env["rma.order.line"]
        if self.lot_ids:
            qty = 0.0
            for lot in self.lot_ids:
                for quant in self.quant_ids:
                    if quant.lot_id == lot:
                        qty += quant.qty
                data = self._prepare_rma_line(rma, qty, lot=lot)
                obj_line.with_context(default_rma_id=rma.id).create(data)
        else:
            data = self._prepare_rma_line(rma, self.product_qty, lot=False)
            obj_line.with_context(default_rma_id=rma.id).create(data)

    @api.multi
    def _prepare_rma_line(self, rma, qty, lot=False):
        operation = self.product_id.product_tmpl_id._get_rma_operation(
            rma.type)
        data = {
            "reference_move_id": self.id,
            "product_id": self.product_id.id,
            "lot_id": lot and lot.id or False,
            "name": self.product_id.name,
            "origin": self.picking_id.name,
            "uom_id": self.product_id.uom_id.id,
            "operation_id": operation.id,
            "product_qty": qty,
            "delivery_address_id": self.picking_id.partner_id.id,
            "rma_id": rma.id
        }

        if not operation:
            raise UserError(_("Please define an operation first"))

        if not operation.in_route_id or not operation.out_route_id:
            route = self.env["stock.location.route"].search(
                [("rma_selectable", "=", True)], limit=1)
            if not route:
                raise UserError(_("Please define an rma route"))
        data.update(
            {"in_route_id": operation.in_route_id.id,
             "out_route_id": operation.out_route_id.id,
             "receipt_policy": operation.receipt_policy,
             "operation_id": operation.id,
             "delivery_policy": operation.delivery_policy
             })
        if operation.in_warehouse_id:
            data["in_warehouse_id"] = operation.in_warehouse_id.id
        if operation.out_warehouse_id:
            data["out_warehouse_id"] = operation.out_warehouse_id.id
        if operation.location_id:
            data["location_id"] = operation.location_id.id
        return data
