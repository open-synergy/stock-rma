# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _create_rma_line(self, rma, operation=False, route_template=False):
        self.ensure_one()
        data = self._prepare_rma_line(
            rma=rma,
            operation=operation,
            route_template=route_template,
        )
        inv_line = self.env["rma.order.line"].create(data)
        return inv_line

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
    def _prepare_rma_line(self, rma, operation=False, route_template=False):
        self.ensure_one()

        if not operation:
            operation = self._get_rma_operation(rma.type)

        if not route_template:
            route_template = self._get_rma_route_template(rma.type)

        data = {
            "invoice_line_id": self.id,
            "product_id": self.product_id.id,
            "origin": self.invoice_id.number,
            "uom_id": self.uos_id.id,
            "operation_id": operation.id,
            "route_template_id": route_template.id,
            "product_qty": self.quantity,
            "price_unit": self.price_unit,  # TODO: Tax?
            "delivery_address_id": self.invoice_id.partner_id.id,
            "invoice_address_id": self.invoice_id.partner_id.id,
            "rma_id": rma.id,
        }

        data.update(operation._get_operation_policy())

        if route_template:
            data.update(route_template._get_route_template_policy())

        return data
