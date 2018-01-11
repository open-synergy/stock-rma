# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime
import csv
import os


class BaseCase(TransactionCase):

    def setUp(self):
        super(BaseCase, self).setUp()
        self.rma_make_picking = self.env['rma_make_picking.wizard']
        self.rma_add_stock_move = self.env['rma_add_stock_move']
        self.make_supplier_rma = self.env["rma.order.line.make.supplier.rma"]
        self.stockpicking = self.env['stock.picking']
        self.rma = self.env['rma.order']
        self.rma_line = self.env['rma.order.line']
        self.rma_op = self.env['rma.operation']
        self.rma_op_id = self.env.ref('rma.rma_operation_customer_replace')
        self.product_id = self.env.ref('product.product_product_4')
        self.product_1 = self.env.ref('product.product_product_25')
        self.product_2 = self.env.ref('product.product_product_30')
        self.product_3 = self.env.ref('product.product_product_33')
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.wh = self.env.ref("stock.warehouse0")
        self.route_customer = self.env.ref("rma.route_rma_customer")
        self.route_supplier = self.env.ref("rma.route_rma_supplier")
        # assign an operation
        product_value = {
            "rma_customer_operation_id": self.rma_op_id.id,
            "rma_supplier_operation_id": self.rma_op_id.id,
        }
        self.product_1.write(product_value)
        self.product_2.write(product_value)
        self.product_3.write(product_value)
        self.partner = self.env.ref('base.res_partner_12')
        self.supplier = self.env.ref('base.res_partner_13')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.stock_rma_location = self.env.ref('rma.location_rma')
        self.customer_location = self.env.ref(
            'stock.stock_location_customers')
        self.supplier_location = self.env.ref(
            'stock.stock_location_suppliers')
        self.product_uom_id = self.env.ref('product.product_uom_unit')
        self.product_uom_id = self.env.ref('product.product_uom_unit')

    def _prepare_rma(self,
                     partner,
                     rma_type,
                     date_rma,
                     rma_lines,
                     ):
        return {
            "partner_id": partner.id,
            "type": rma_type,
            "date_rma": date_rma,
            "rma_line_ids": rma_lines,
        }

    def _prepare_rma_lines(self,
                           operation,
                           product=False,
                           qty=7.0,
                           price_unit=0.0,
                           ):
        if not product:
            product = self.product_1

        location = operation.location_id or \
            operation.in_warehouse_id.lot_rma_id

        return {
            "operation_id": operation.id,
            "product_id": product.id,
            "product_qty": qty,
            "uom_id": product.uom_id.id,
            "price_unit": price_unit,
            "customer_to_supplier": operation.customer_to_supplier,
            "supplier_to_customer": operation.supplier_to_customer,
            "receipt_policy_id": operation.receipt_policy_id.id,
            "delivery_policy_id": operation.delivery_policy_id.id,
            "rma_supplier_policy_id": operation.rma_supplier_policy_id.id,
            "in_route_id": operation.in_route_id.id,
            "out_route_id": operation.out_route_id.id,
            "in_warehouse_id": operation.in_warehouse_id.id,
            "out_warehouse_id": operation.out_warehouse_id.id,
            "location_id": location.id,
            "supplier_address_id": self.supplier.id,
        }

    def _create_rma(self,
                    operation=False,
                    partner=False,
                    rma_type="customer",
                    date_rma=datetime.now().strftime("%Y-%m-%d %H:%S:%M"),
                    rma_lines=False):
        if not partner:
            partner = self.partner
        if not operation:
            operation = self.rma_op_id
        if not rma_lines:
            rma_lines = []
            rma_lines.append((0, 0, self._prepare_rma_lines(operation)))
        rma = self.rma.create(self._prepare_rma(
            partner,
            rma_type,
            date_rma,
            rma_lines))
        return rma

    def _rma_request_approval(self, rma):
        rma.action_rma_to_approve()

    def _rma_approve(self, rma):
        rma.action_rma_approve()

    def _rma_done(self, rma):
        rma.action_rma_done()

    def _rma_draft(self, rma):
        rma.action_rma_draft()

    def _process_move(self, moves):
        for move in moves:
            if move.state not in ["done", "cancel"]:
                move.action_done()

    def _check_rma_line_shipment(
            self,
            rma_line,
            in_shipment=False,
            out_shipment=False,
    ):
        if in_shipment:
            self.assertEqual(
                rma_line.in_shipment_count,
                in_shipment)
        if out_shipment:
            self.assertEqual(
                rma_line.out_shipment_count,
                out_shipment)

    def _check_rma_shipment(
            self,
            rma,
            in_shipment=False,
            out_shipment=False,
    ):
        if in_shipment:
            self.assertEqual(
                rma.in_shipment_count,
                in_shipment)
        if out_shipment:
            self.assertEqual(
                rma.out_shipment_count,
                out_shipment)

    def _check_quantity(self,
                        rma_line,
                        qty_to_receive=False, qty_incoming=False,
                        qty_received=False, qty_to_deliver=False,
                        qty_outgoing=False, qty_delivered=False,
                        qty_to_supplier_rma=False, qty_in_supplier_rma=False):
        if qty_to_receive:
            self.assertEqual(
                qty_to_receive,
                rma_line.qty_to_receive)
        if qty_incoming:
            self.assertEqual(
                qty_incoming,
                rma_line.qty_incoming)
        if qty_received:
            self.assertEqual(
                qty_received,
                rma_line.qty_received)
        if qty_to_deliver:
            self.assertEqual(
                qty_to_deliver,
                rma_line.qty_to_deliver)
        if qty_outgoing:
            self.assertEqual(
                qty_outgoing,
                rma_line.qty_outgoing)
        if qty_delivered:
            self.assertEqual(
                qty_delivered,
                rma_line.qty_delivered)
        if qty_to_supplier_rma:
            self.assertEqual(
                qty_to_supplier_rma,
                rma_line.qty_to_supplier_rma)
        if qty_in_supplier_rma:
            self.assertEqual(
                qty_in_supplier_rma,
                rma_line.qty_in_supplier_rma)

    def _run_qty_check(self, line, file_name):
        script_dir = os.path.dirname(__file__)
        abs_path = os.path.join(script_dir, file_name)
        with open(abs_path, "rb") as csvfile:
            scenarios = csv.DictReader(csvfile, delimiter=",")
            for row in scenarios:
                receipt_policy_id = self.env.ref(
                    row["receipt_policy_xml_id"]).id
                delivery_policy_id = self.env.ref(
                    row["delivery_policy_xml_id"]).id
                rma_supplier_policy_id = self.env.ref(
                    row["rma_supplier_policy_xml_id"]).id
                line.write({
                    "receipt_policy_id": receipt_policy_id,
                    "delivery_policy_id": delivery_policy_id,
                    "rma_supplier_policy_id": rma_supplier_policy_id,
                })
                self._check_quantity(
                    line,
                    qty_to_supplier_rma=float(row["qty_to_supplier_rma"]),
                    qty_to_receive=float(row["qty_to_receive"]),
                    qty_to_deliver=float(row["qty_to_deliver"]),
                )
