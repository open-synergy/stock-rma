# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)..

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rma_line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA",
        ondelete="restrict",
    )

    @api.multi
    def _create_rma_line_from_so_line(
            self, rma, operation=False, route_template=False):
        self.ensure_one()
        data = self._prepare_rma_line_from_so_line(
            rma=rma, operation=operation, route_template=route_template)
        so_line = self.env["rma.order.line"].create(data)
        return so_line

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        # TODO: Review
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        vals.update({
            "rma_line_id": self.rma_line_id.id
        })
        return vals

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
    def _prepare_rma_line_from_so_line(
            self, rma, operation=False, route_template=False):
        self.ensure_one()

        if not operation:
            operation = self._get_rma_operation(rma.type)

        if not route_template:
            route_template = self._get_rma_route_template(rma.type)

        data = {
            "sale_line_id": self.id,
            "product_id": self.product_id.id,
            "origin": self.order_id.name,
            "uom_id": self.product_uom.id,
            "operation_id": operation.id,
            "sale_policy_id": operation.sale_policy_id.id,
            "route_template_id": route_template.id,
            "product_qty": self.product_uom_qty,
            "delivery_address_id": self.order_id.partner_id.id,
            "invoice_address_id": self.order_id.partner_id.id,
            "currency_id": self.order_id.currency_id.id,
            "price_unit": self.price_unit,
            "rma_id": rma.id,
        }

        data.update(operation._get_operation_policy())

        if route_template:
            data.update(route_template._get_route_template_policy())

        return data
