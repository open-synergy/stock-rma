# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class RmaOperation(models.Model):
    _name = "rma.operation"
    _description = "RMA Operation"

    @api.model
    def _default_warehouse_id(self):
        company_id = self.env.user.company_id.id
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company_id)], limit=1)
        return warehouse

    @api.model
    def _default_customer_location_id(self):
        return self.env.ref("stock.stock_location_customers") or False

    @api.model
    def _default_supplier_location_id(self):
        return self.env.ref("stock.stock_location_suppliers") or False

    @api.model
    def _default_receipt_policy(self):
        try:
            result = self.env.ref("rma.rma_policy_no")
        except ValueError:
            result = self.env["rma.policy"]._create_default_policy()
        return result

    @api.model
    def _default_delivery_policy(self):
        try:
            result = self.env.ref("rma.rma_policy_no")
        except ValueError:
            result = self.env["rma.policy"]._create_default_policy()
        return result

    @api.model
    def _default_rma_supplier_policy(self):
        try:
            result = self.env.ref("rma.rma_policy_no")
        except ValueError:
            result = self.env["rma.policy"]._create_default_policy()
        return result

    name = fields.Char(
        string="Description",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        required=False,
        default=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    receipt_policy_id = fields.Many2one(
        string="Receipt Policy",
        comodel_name="rma.policy",
        domain=[
            ("receipt_policy_ok", "=", True),
        ],
        required=True,
        default=lambda self: self._default_receipt_policy(),
    )
    delivery_policy_id = fields.Many2one(
        string="Delivery Policy",
        comodel_name="rma.policy",
        domain=[
            ("delivery_policy_ok", "=", True),
        ],
        required=True,
        default=lambda self: self._default_delivery_policy(),
    )
    rma_supplier_policy_id = fields.Many2one(
        string="RMA Supplier Policy",
        comodel_name="rma.policy",
        domain=[
            ("rma_type", "in", ["both", "customer"]),
            ("rma_supplier_policy_ok", "=", True),
        ],
        required=True,
        default=lambda self: self._default_receipt_policy(),
    )
    in_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Inbound Route",
        domain=[
            ("rma_selectable", "=", True),
        ],
    )
    out_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Outbound Route",
        domain=[
            ("rma_selectable", "=", True),
        ],
    )
    type = fields.Selection(
        selection=[
            ("customer", "Customer"),
            ("supplier", "Supplier"),
        ],
        string="Used in RMA of this type",
        required=True,
        default="customer",
    )
    rma_line_ids = fields.One2many(
        comodel_name="rma.order.line",
        inverse_name="operation_id",
        string="RMA lines",
    )
    default_route_template_id = fields.Many2one(
        string="Default Route Template",
        comodel_name="rma.route_template",
    )
    allowed_route_template_ids = fields.Many2many(
        string="Allowed Route Templates",
        comodel_name="rma.route_template",
        relation="rel_rma_operation_2_route_template",
        column1="operation_id",
        column2="route_template_id",
    )

    @api.multi
    def _get_operation_policy(self):
        return {
            "receipt_policy_id": self.receipt_policy_id.id,
            "delivery_policy_id": self.delivery_policy_id.id,
        }
