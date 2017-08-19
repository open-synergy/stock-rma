# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseCase


class TestRmaOperation(BaseCase):

    def setUp(self):
        super(TestRmaOperation, self).setUp()

    def test_default_warehouse_id(self):
        wh_default = self.rma_op._default_warehouse_id()
        self.assertEqual(
            wh_default,
            self.wh)

    def test_default_customer_location_id(self):
        loc = self.rma_op._default_customer_location_id()
        self.assertEqual(
            loc,
            self.customer_location)

    def test_default_supplier_location_id(self):
        loc = self.rma_op._default_supplier_location_id()
        self.assertEqual(
            loc,
            self.supplier_location)
