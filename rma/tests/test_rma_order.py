# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import BaseCase


class TestRmaOrder(BaseCase):

    def setUp(self):
        super(TestRmaOrder, self).setUp()

    def test_default_type(self):
        rma_type = self.rma._get_default_type()
        self.assertEqual(
            rma_type,
            "customer")

        rma_type = self.rma.with_context(supplier=1)._get_default_type()
        self.assertEqual(
            rma_type,
            "supplier")
