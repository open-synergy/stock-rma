# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.rma.tests.base import BaseCase
from datetime import datetime


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
        self.obj_wiz_add_so = self.env["rma_add_sale"]

    def _prepare_so(self):
        pricelist = self.partner.property_product_pricelist
        return {
            "partner_id": self.partner.id,
            "date_order": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "warehouse_id": self.wh.id,
            "pricelist_id": pricelist.id,
            "currency_id": pricelist.currency_id.id,
            "order_line": [(0, 0, {
                "product_id": self.product_1.id,
                "name": self.product_1.name,
                "product_uom_qty": 7.0,
                "product_uom": self.product_1.uom_id.id,
                "price_unit": 700.00,
            })]
        }

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
        so = self.env["sale.order"].create(
            self._prepare_so())
        so.signal_workflow("order_confirm")
        rma = self._create_rma(rma_type="customer", rma_lines=[])
        wiz = self.obj_wiz_add_so.create({
            "rma_id": rma.id,
            "partner_id": self.partner.id,
            "sale_id": so.id,
            "sale_line_ids": [(6, 0, so.order_line.ids)],
        })
        wiz.add_lines()
        self._rma_request_approval(rma)
        self._rma_approve(rma)
        line = rma.rma_line_ids[0]
        # self._check_quantity(
        #     line,
        #     qty_to_receive=7.0,
        #     qty_to_refund=0.0)
        rma.action_view_sale_order()
        line.action_view_sale_order()
