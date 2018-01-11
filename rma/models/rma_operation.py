# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


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
        return self.env.ref("rma.rma_policy_no") or False

    @api.model
    def _default_delivery_policy(self):
        return self.env.ref("rma.rma_policy_no") or False

    @api.model
    def _default_rma_supplier_policy(self):
        return self.env.ref("rma.rma_policy_no") or False

    name = fields.Char(
        string="Description",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        required=True,
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
    customer_to_supplier = fields.Boolean(
        string="The customer will send to the supplier",
        default=False,
    )
    supplier_to_customer = fields.Boolean(
        string="The supplier will send to the customer",
        default=False,
    )
    in_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Inbound Warehouse",
        default=lambda self: self._default_warehouse_id(),
    )
    out_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Outbound Warehouse",
        default=lambda self: self._default_warehouse_id(),
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Send To This Company Location",
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
