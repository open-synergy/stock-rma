# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseCase
import csv
import os


class TestRmaCustomer(BaseCase):

    def setUp(self):
        super(TestRmaCustomer, self).setUp()

        self.cust_op = self.rma_op.create({
            "name": "Test RMA Operation",
            "code": "TEST",
            "receipt_policy_id": self.env.\
                ref("rma.rma_policy_no").id,
            "delivery_policy_id": self.env.\
                ref("rma.rma_policy_no").id,
            "rma_supplier_policy_id": self.env.\
                ref("rma.rma_policy_no").id,
            "type": "customer",
            "in_warehouse_id": self.wh.id,
            "out_warehouse_id": self.wh.id,
            "in_route_id": self.route_customer.id,
            "out_route_id": self.route_customer.id,
            "location_id": self.stock_rma_location.id,
        })

    def test_customer_rma(self):
        # Create and Approve RMA
        rma = self._create_rma(
            operation=self.cust_op,
            rma_type="customer",
        )
        self._rma_request_approval(rma)
        self._rma_approve(rma)
        line = rma.rma_line_ids[0]

        # Create Incoming Picking
        wiz = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "incoming"
        }).create({})
        wiz_item = wiz.item_ids[0]
        wiz_item.qty_to_receive = 5.0
        wiz.action_create_picking()
        self._process_move(line.move_ids)
        self._check_quantity(
            line,
            qty_received=5.0
            )
        self._run_qty_check(line, "rma_customer_case_01.csv")

        # Create Outgoing Picking
        wiz_out_1 = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "outgoing"
        }).create({})
        wiz_item = wiz_out_1.item_ids[0]
        wiz_item.qty_to_deliver = 3.0
        wiz_out_1.action_create_picking()
        self._process_move(line.move_ids)
        self._check_quantity(
            line,
            qty_delivered=3.0
            )

        # Make supplier RMA
        wiz = self.make_supplier_rma.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
        }).create({})
        wiz.item_ids[0].product_qty = 2.0
        wiz.make_supplier_rma()
        self._check_quantity(
            line,
            qty_in_supplier_rma=2.0
            )

        self._run_qty_check(line, "rma_customer_case_99.csv")
                    
        # Done RMA
        self._rma_done(rma)

        # Line's action
        line.action_view_in_shipments()
        line.action_view_out_shipments()
        line.action_view_procurements()

        # RMA's action
        rma.action_view_lines()
        rma.action_view_supplier_lines()
        rma.action_view_in_shipments()
        rma.action_view_out_shipments()
