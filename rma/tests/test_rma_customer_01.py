# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseCase


class TestRmaCustomer(BaseCase):

    def setUp(self):
        super(TestRmaCustomer, self).setUp()

        self.cust_op = self.rma_op.create({
            "name": "Delivery BeforeReceive",
            "code": "RAR",
            "receipt_policy_id": self.env.ref("rma.rma_policy_delivered_received").id,
            "delivery_policy_id": self.env.ref("rma.rma_policy_ordered_delivered").id,
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
            qty_to_receive=0.0,
            qty_received=0.0,
            qty_incoming=0.0,
            qty_to_deliver=7.0,
            qty_delivered=0.0,
            qty_outgoing=0.0,
        )
        wiz_out_1 = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "outgoing"
        }).create({})
        wiz_item = wiz_out_1.item_ids[0]
        wiz_item.qty_to_deliver = 3.0
        wiz_out_1.action_create_picking()
        self._check_quantity(
            line,
            qty_to_receive=0.0,
            qty_received=0.0,
            qty_incoming=0.0,
            qty_to_deliver=7.0,
            qty_delivered=0.0,
            qty_outgoing=3.0,
        )
        self._process_move(line.move_ids)
        self._check_quantity(
            line,
            qty_to_receive=3.0,
            qty_received=0.0,
            qty_incoming=0.0,
            qty_to_deliver=4.0,
            qty_delivered=3.0,
            qty_outgoing=0.0,
        )
        wiz_in_1 = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "incoming"
        }).create({})
        wiz_in_1.item_ids[0].qty_to_receive = 2.0
        wiz_in_1.action_create_picking()
        self._check_quantity(
            line,
            qty_to_receive=3.0,
            qty_received=0.0,
            qty_incoming=2.0,
            qty_to_deliver=4.0,
            qty_delivered=3.0,
            qty_outgoing=0.0,
        )
        self._process_move(line.move_ids)
        self._check_quantity(
            line,
            qty_to_receive=1.0,
            qty_received=2.0,
            qty_incoming=0.0,
            qty_to_deliver=4.0,
            qty_delivered=3.0,
            qty_outgoing=0.0,
        )
        # wiz_out_2 = self.rma_make_picking.with_context({
        #     "active_model": "rma.order.line",
        #     "active_ids": [line.id],
        #     "picking_type": "outgoing"
        # }).create({})
        # wiz_item = wiz_out_2.item_ids[0]
        # wiz_item.qty_to_deliver = 1.0
        # wiz_out_2.action_create_picking()
        # self._check_quantity(
        #     line,
        #     qty_to_receive=4.0,
        #     qty_received=3.0,
        #     qty_incoming=0.0,
        #     qty_to_deliver=1.0,
        #     qty_delivered=2.0,
        #     qty_outgoing=1.0,
        # )
        # self._check_shipment(
        #     line,
        #     in_shipment=1,
        #     out_shipment=2,
        # )
        # self._process_move(line.move_ids)
        # self._check_quantity(
        #     line,
        #     qty_to_receive=4.0,
        #     qty_received=3.0,
        #     qty_incoming=0.0,
        #     qty_to_deliver=0.0,
        #     qty_delivered=3.0,
        #     qty_outgoing=0.0,
        # )
        self._rma_done(rma)
