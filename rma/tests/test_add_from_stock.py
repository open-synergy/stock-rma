# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseCase


class TestRmaOrder(BaseCase):

    def setUp(self):
        super(TestRmaOrder, self).setUp()
        self.obj_picking = self.env["stock.picking"]

    def _prepare_out_picking_data(self):
        return {
            "picking_type_id": self.wh.out_type_id.id,
            "move_lines": [
                (0, 0, {
                    "name": self.product_1.name,
                    "product_id": self.product_1.id,
                    "product_uom_qty": 7.0,
                    "product_uom": self.product_1.uom_id.id,
                    "location_id": self.wh.lot_stock_id.id,
                    "location_dest_id": self.wh.wh_output_stock_loc_id.id,
                }),
            ],
        }

    def test_create_from_stock_move(self):
        out_picking = self.obj_picking.create(
            self._prepare_out_picking_data())
        out_picking.action_confirm()
        out_picking.action_assign()
        out_picking.action_done()
        rma = self._create_rma(rma_lines=[])
        wiz = self.rma_add_stock_move.with_context({
            "active_model": "rma.order",
            "active_ids": [rma.id]}).create({
                "move_ids": [(6, 0, out_picking.move_lines.ids)],
            })
        wiz.add_lines()
        self._rma_request_approval(rma)
        self._rma_approve(rma)
        self._check_quantity(
            rma.rma_line_ids[0],
            qty_to_receive=7.0,
            qty_received=0.0,
            qty_incoming=0.0,
            qty_to_deliver=0.0,
            qty_delivered=0.0,
            qty_outgoing=0.0,
        )
