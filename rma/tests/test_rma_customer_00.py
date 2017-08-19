# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseCase


class TestRmaCustomer(BaseCase):

    def setUp(self):
        super(TestRmaCustomer, self).setUp()

        self.cust_op = self.rma_op.create({
            "name": "Replace After Receive",
            "code": "RAR",
            "receipt_policy": "ordered",
            "delivery_policy": "received",
            "type": "customer",
            "in_warehouse_id": self.wh.id,
            "out_warehouse_id": self.wh.id,
            "in_route_id": self.route_customer.id,
            "out_route_id": self.route_customer.id,
            "location_id": self.stock_rma_location.id,
        })

    def test_customer_rma(self):
        rma = self._create_rma(
            operation=self.cust_op,
            rma_type="customer",
        )
        self._rma_request_approval(rma)
        self._rma_approve(rma)
        line = rma.rma_line_ids[0]
        self._check_quantity(
            line,
            qty_to_receive=7.0,
            qty_received=0.0,
            qty_incoming=0.0,
            qty_to_deliver=0.0,
            qty_delivered=0.0,
            qty_outgoing=0.0,
        )
        wiz = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "incoming"
        }).create({})
        wiz_item = wiz.item_ids[0]
        wiz_item.qty_to_receive = 3.0
        wiz.action_create_picking()
        self._check_shipment(
            line,
            in_shipment=1)
        self.assertEqual(
            len(line.move_ids),
            1)
        self._check_quantity(
            line,
            qty_to_receive=7.0,
            qty_received=0.0,
            qty_incoming=3.0,
            qty_to_deliver=0.0,
            qty_delivered=0.0,
            qty_outgoing=0.0,
        )
        self._process_move(line.move_ids[0])
        self._check_quantity(
            line,
            qty_to_receive=4.0,
            qty_received=3.0,
            qty_incoming=0.0,
            qty_to_deliver=3.0,
            qty_delivered=0.0,
            qty_outgoing=0.0,
        )
        wiz_out_1 = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "outgoing"
        }).create({})
        wiz_item = wiz_out_1.item_ids[0]
        wiz_item.qty_to_deliver = 2.0
        wiz_out_1.action_create_picking()
        self._check_quantity(
            line,
            qty_to_receive=4.0,
            qty_received=3.0,
            qty_incoming=0.0,
            qty_to_deliver=3.0,
            qty_delivered=0.0,
            qty_outgoing=2.0,
        )
        self._check_shipment(
            line,
            in_shipment=1,
            out_shipment=1,
        )
        self._process_move(line.move_ids[0])
        self._check_quantity(
            line,
            qty_to_receive=4.0,
            qty_received=3.0,
            qty_incoming=0.0,
            qty_to_deliver=1.0,
            qty_delivered=2.0,
            qty_outgoing=0.0,
        )
        self._rma_done(rma)
