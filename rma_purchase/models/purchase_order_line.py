# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class PurchaserOderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _create_rma_line_from_po_line(
            self, rma, operation=False, route_template=False):
        self.ensure_one()
        data = self._prepare_rma_line_from_po_line(
            rma=rma, operation=operation, route_template=route_template)
        po_line = self.env["rma.order.line"].create(data)
        return po_line

    @api.multi
    def _get_rma_operation(self, rma_type):
        self.ensure_one()
        operation = self.product_id.product_tmpl_id._get_rma_operation(
            rma_type)
        if not operation:
            raise UserError(_("Please define an operation first"))
        return operation

    @api.multi
    def _get_rma_route_template(self, rma_type):
        self.ensure_one()
        route_template = False
        if not route_template:
            raise UserError(_("Please define an route template first"))
        return route_template

    @api.multi
    def _prepare_rma_line_from_po_line(
            self, rma, operation=False, route_template=False):
        self.ensure_one()

        if not operation:
            operation = self._get_rma_operation(rma.type)

        if not route_template:
            route_template = self._get_rma_route_template(rma.type)

        data = {
            "purchase_order_line_id": self.id,
            "product_id": self.product_id.id,
            "origin": self.order_id.name,
            "uom_id": self.product_uom.id,
            "operation_id": operation.id,
            "route_template_id": route_template.id,
            "product_qty": self.product_qty,
            "price_unit": self.price_unit,
            "currency_id": self.order_id.currency_id.id,
            "rma_id": rma.id,
        }

        data.update(operation._get_operation_policy())

        if route_template:
            data.update(route_template._get_route_template_policy())

        return data
