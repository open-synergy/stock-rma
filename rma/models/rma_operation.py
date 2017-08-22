# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
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
    receipt_policy = fields.Selection(
        selection=[
            ("no", "Not required"),
            ("ordered", "Based on Ordered Quantities"),
            # ("received", "Based on Delivered Quantities"),
            ("delivered", "Based on Delivered Quantities"),
        ],
        string="Receipts Policy",
        default="no",
    )
    delivery_policy = fields.Selection(
        selection=[
            ("no", "Not required"),
            ("ordered", "Based on Ordered Quantities"),
            ("received", "Based on Received Quantities"),
        ],
        string="Delivery Policy",
        default="no",
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
