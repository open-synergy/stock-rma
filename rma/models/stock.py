# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
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
        # if vals.get("procurement_id"):
        #     procurement = self.env["procurement.order"].browse(
        #         vals["procurement_id"])
        #     if procurement.rma_line_id:
        #         vals["rma_line_id"] = procurement.rma_line_id.id
        return super(StockMove, self).create(vals)

    @api.multi
    def _create_rma_line(self, rma, operation=False, route_template=False):
        self.ensure_one()
        obj_line = self.env["rma.order.line"]
        if self.lot_ids:
            qty = 0.0
            for lot in self.lot_ids:
                for quant in self.quant_ids:
                    if quant.lot_id == lot:
                        qty += quant.qty
                data = self._prepare_rma_line(
                    rma=rma,
                    qty=qty,
                    lot=lot,
                    operation=operation,
                    route_template=route_template,
                )
                obj_line.with_context(default_rma_id=rma.id).create(data)
        else:
            data = self._prepare_rma_line(
                rma=rma,
                qty=self.product_qty,
                lot=False,
                operation=operation,
                route_template=route_template,
            )
            obj_line.with_context(default_rma_id=rma.id).create(data)

    @api.multi
    def _get_rma_operation(self, rma_type):
        self.ensure_one()
        operation = self.product_id.product_tmpl_id._get_rma_operation(
            rma_type)
        if not operation:
            raise UserError(_("Please define an operation first"))
        return operation

    @api.multi
    def _get_rma_route_template(self, rma_type):
        self.ensure_one()
        route_template = False
        if not route_template:
            raise UserError(_("Please define an route template first"))
        return route_template

    @api.multi
    def _prepare_rma_line(self, rma, qty, lot=False,
                          operation=False, route_template=False):
        self.ensure_one()

        if not operation:
            operation = self._get_rma_operation(rma.type)

        data = {
            "reference_move_id": self.id,
            "product_id": self.product_id.id,
            "lot_id": lot and lot.id or False,
            "name": self.product_id.name,
            "origin": self.picking_id.name,
            "uom_id": self.product_id.uom_id.id,
            "operation_id": operation.id,
            "route_template_id": route_template.id,
            "product_qty": qty,
            "delivery_address_id": self.picking_id.partner_id.id,
            "rma_id": rma.id
        }

        data.update(operation._get_operation_policy())

        if route_template:
            data.update(route_template._get_route_template_policy())

        return data
