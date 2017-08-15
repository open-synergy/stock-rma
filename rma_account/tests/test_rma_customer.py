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

    def _check_quantity(
            self, rma_line,
            qty_to_receive=False, qty_incoming=False,
            qty_received=False, qty_to_deliver=False,
            qty_outgoing=False, qty_delivered=False,
            qty_to_supplier_rma=False, qty_in_supplier_rma=False,
            qty_to_refund=False, qty_refunded=False):
        super(TestRmaCustomer, self)._check_quantity(
            rma_line=rma_line,
            qty_to_receive=qty_to_receive, qty_incoming=qty_incoming,
            qty_received=qty_received, qty_to_deliver=qty_to_deliver,
            qty_outgoing=qty_outgoing, qty_delivered=qty_delivered)
        if not qty_to_refund:
            self.assertEqual(
                qty_to_refund,
                rma_line.qty_to_refund)
        if not qty_refunded:
            self.assertEqual(
                qty_refunded,
                rma_line.qty_refunded)

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
        self._check_quantity(
            line,
            qty_to_receive=7.0,
            qty_to_refund=0.0)
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
        self._check_quantity(line,
                             qty_incoming=3.0)
        self._process_move(line.move_ids[0])
        self._check_quantity(
            line,
            qty_to_receive=4.0,
            qty_received=3.0,
            qty_to_refund=3.0,
            qty_incoming=0.0)
        wiz_refund = self.obj_wiz_refund.with_context({
            "active_model": "rma.order.line",
            "active_ids": [line.id],
        }).create({})
        wiz_refund.item_ids[0].qty_to_refund = 2.0
        wiz_refund.invoice_refund()
        line.refund_line_ids.invoice_id.signal_workflow("invoice_open")
        self._check_quantity(
            line,
            qty_to_refund=1.0,
            qty_refunded=2.0)
        self._rma_done(rma)
