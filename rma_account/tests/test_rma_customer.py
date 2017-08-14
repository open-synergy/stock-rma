# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.rma.tests.base import BaseCase


class TestRmaCustomer(BaseCase):
    def setUp(self):
        super(TestRmaCustomer, self).setUp()

        self.rar_op = self.rma_op.create({
            "name": "Refund After Receive",
            "code": "RAR",
            "refund_policy": "received",
            "receipt_policy": "ordered",
            "delivery_policy": "no",
            "type": "customer",
            "in_warehouse_id": self.wh.id,
            "out_warehouse_id": self.wh.id,
            "in_route_id": self.route_customer.id,
            "out_route_id": self.route_customer.id,
            "location_id": self.stock_rma_location.id,
            })
        self.obj_wiz_refund = self.env["rma.refund"]

    def test_rma_creation(self):
        line_data = self._prepare_rma_lines(
            self.rar_op)
        line_data.update({"refund_policy": self.rar_op.refund_policy})
        rma = self._create_rma(
            operation=self.rar_op,
            rma_type="customer",
            rma_lines=[(0, 0, line_data)])
        self._rma_request_approval(rma)
        self._rma_approve(rma)
        line = rma.rma_line_ids[0]
        self.assertEqual(
            line.qty_to_receive,
            7.0)
        self.assertEqual(
            line.qty_to_refund,
            0.0)
        wiz = self.rma_make_picking.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            "picking_type": "incoming"
            }).create({})
        wiz_item = wiz.item_ids[0]
        wiz_item.qty_to_receive = 3.0
        wiz.action_create_picking()
        self.assertEqual(
            len(line.move_ids),
            1)
        self.assertEqual(
            line.qty_incoming,
            3.0)
        self._process_move(line.move_ids[0])
        self.assertEqual(
            line.qty_to_receive,
            4.0)
        self.assertEqual(
            line.qty_incoming,
            0.0)
        self.assertEqual(
            line.move_ids[0].product_uom_qty,
            3.0)
        self.assertEqual(
            line.qty_received,
            3.0)
        self.assertEqual(
            line.qty_to_refund,
            3.0)
        wiz_refund = self.obj_wiz_refund.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
            }).create({})
        wiz_refund.item_ids[0].qty_to_refund = 2.0
        wiz_refund.invoice_refund()
        line.refund_line_ids.invoice_id.signal_workflow("invoice_open")
        self.assertEqual(
            line.qty_to_refund,
            1.0)
        self.assertEqual(
            line.qty_refunded,
            2.0)

        self._rma_done(rma)
