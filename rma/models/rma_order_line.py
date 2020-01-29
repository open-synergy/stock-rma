# Copyright (C) 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
import operator
ops = {"=": operator.eq,
       "!=": operator.ne}


class RmaOrderLine(models.Model):
    _name = "rma.order.line"
    _description = "RMA Order Line"
    _rec_name = "rma_id"

    @api.model
    def _default_warehouse_id(self):
        rma_id = self.env.context.get("default_rma_id", False)
        warehouse = self.env["stock.warehouse"]
        if rma_id:
            rma = self.env["rma.order"].browse(rma_id)
            warehouse = self.env["stock.warehouse"].search(
                [("company_id", "=", rma.company_id.id)], limit=1)
        return warehouse

    @api.model
    def _default_location_id(self):
        wh = self._default_warehouse_id()
        return wh.lot_rma_id

    @api.model
    def _default_delivery_address(self):
        partner_id = self.env.context.get("partner_id", False)
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            addr = partner.address_get(["delivery"])
            return self.env["res.partner"].browse(addr["delivery"])
        return False

    @api.multi
    def _compute_in_shipment_count(self):
        for line in self:
            picking_ids = []
            for move in line.move_ids:
                if move.location_dest_id.usage == "internal":
                    picking_ids.append(move.picking_id.id)
                else:
                    if line.customer_to_supplier:
                        picking_ids.append(move.picking_id.id)
            shipments = list(set(picking_ids))
            line.in_shipment_count = len(shipments)

    @api.multi
    def _compute_out_shipment_count(self):
        picking_ids = []
        for line in self:
            for move in line.move_ids:
                if move.location_dest_id.usage in ("supplier", "customer"):
                    if not line.customer_to_supplier:
                        picking_ids.append(move.picking_id.id)
            shipments = list(set(picking_ids))
            line.out_shipment_count = len(shipments)

    @api.multi
    def _get_rma_move_qty(self, states, direction="in"):
        for rec in self:
            product_obj = self.env["product.uom"]
            qty = 0.0
            if direction == "in":
                op = ops["="]
            else:
                op = ops["!="]
            for move in rec.move_ids.filtered(
                    lambda m: m.state in states and op(m.location_id.usage,
                                                       rec.type)):
                qty += product_obj._compute_quantity(
                    move.product_uom_qty, rec.uom_id)
            return qty

    @api.multi
    @api.depends(
        "move_ids",
        "move_ids.state",
        "type",
    )
    def _compute_qty_incoming(self):
        for rec in self:
            qty = rec._get_rma_move_qty(
                ("draft", "confirmed", "assigned"), direction="in")
            rec.qty_incoming = qty

    @api.multi
    @api.depends(
        "move_ids",
        "move_ids.state",
        "type",
    )
    def _compute_qty_received(self):
        for rec in self:
            qty = rec._get_rma_move_qty("done", direction="in")
            rec.qty_received = qty

    @api.multi
    @api.depends(
        "move_ids",
        "move_ids.state",
        "type",
    )
    def _compute_qty_outgoing(self):
        for rec in self:
            qty = rec._get_rma_move_qty(
                ("draft", "confirmed", "assigned"), direction="out")
            rec.qty_outgoing = qty

    @api.multi
    @api.depends(
        "move_ids",
        "move_ids.state",
        "type",
    )
    def _compute_qty_delivered(self):
        for rec in self:
            qty = rec._get_rma_move_qty("done", direction="out")
            rec.qty_delivered = qty

    @api.model
    def _get_supplier_rma_qty(self):
        return sum(self.supplier_rma_line_ids.filtered(
            lambda r: r.state != "cancel").mapped(
            "product_qty"))

    @api.multi
    @api.depends(
        "supplier_rma_line_ids",
        "supplier_rma_line_ids.rma_id.state",
    )
    def _compute_qty_in_supplier_rma(self):
        for rec in self:
            qty = rec._get_supplier_rma_qty()
            rec.qty_in_supplier_rma = qty

    @api.multi
    @api.depends(
        "receipt_policy_id",
        "delivery_policy_id",
        "rma_supplier_policy_id",
        "type",
        "product_qty",
        "qty_received",
        "qty_delivered",
        "qty_in_supplier_rma",
    )
    def _compute_qty_to_receive(self):
        for rec in self:
            rec.qty_to_receive = rec.receipt_policy_id._compute_quantity(rec)

    @api.multi
    @api.depends(
        "receipt_policy_id",
        "delivery_policy_id",
        "rma_supplier_policy_id",
        "type",
        "product_qty",
        "qty_received",
        "qty_delivered",
        "qty_in_supplier_rma",
    )
    def _compute_qty_to_deliver(self):
        for rec in self:
            rec.qty_to_deliver = rec.delivery_policy_id._compute_quantity(rec)

    @api.multi
    @api.depends(
        "receipt_policy_id",
        "delivery_policy_id",
        "rma_supplier_policy_id",
        "type",
        "product_qty",
        "qty_received",
        "qty_delivered",
        "qty_in_supplier_rma",
    )
    def _compute_qty_supplier_rma(self):
        for rec in self:
            rec.qty_to_supplier_rma = rec.rma_supplier_policy_id.\
                _compute_quantity(rec)

    # @api.multi
    # def _compute_procurement_count(self):
    #     for rec in self:
    #         rec.procurement_count = len(rec.procurement_ids.filtered(
    #             lambda p: p.state == "exception"))

    @api.multi
    @api.depends(
        "operation_id",
    )
    def _compute_allowed_route_template_ids(self):
        for document in self:
            result = []
            if document.operation_id:
                result = document.operation_id.allowed_route_template_ids.ids
            document.allowed_route_template_ids = result

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

    delivery_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner delivery address",
        default=lambda self: self._default_delivery_address(),
        help="This address will be used to "
        "deliver repaired or replacement products.",
    )
    rma_id = fields.Many2one(
        comodel_name="rma.order",
        string="RMA",
        ondelete="cascade",
        required=True,
    )
    name = fields.Char(
        string="Reference",
        required=True,
        default="/",
        help="Add here the supplier RMA #. Otherwise an "
        "internal code is assigned.",
    )
    description = fields.Text(
        string="Description",
    )
    origin = fields.Char(
        string="Source Document",
        help="Reference of the document that produced "
        "this rma.",
    )
    state = fields.Selection(
        related="rma_id.state",
    )
    date_rma = fields.Datetime(
        string="Order Date",
        index=True,
        readonly=True,
        related="rma_id.date_rma",
        store=True,
    )
    date_deadline = fields.Datetime(
        string="Deadline",
        index=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Operation",
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="rma_id.assigned_to",
        store=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="rma_id.requested_by",
        store=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="rma_id.partner_id",
        store=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Gives the sequence of this line "
        "when displaying the rma.",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        ondelete="restrict",
        required=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial Number",
        readonly=True,
        states={
            "new": [
                ("readonly", False),
            ],
        },
    )
    product_qty = fields.Float(
        string="Ordered Qty",
        copy=False,
        default=1.0,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    uom_id = fields.Many2one(
        comodel_name="product.uom",
        string="Unit of Measure",
        required=True,
    )
    price_unit = fields.Float(
        string="Price Unit",
        readonly=False,
        states={
            "approved": [
                ("readonly", True),
            ],
            "done": [
                ("readonly", True),
            ],
            "to_approve": [
                ("readonly", True),
            ],
        },
    )
    # procurement_count = fields.Integer(
    #     compute=_compute_procurement_count,
    #     string="# of Procurements",
    #     copy=False,
    #     default=0,
    # )
    in_shipment_count = fields.Integer(
        compute=_compute_in_shipment_count,
        string="# of Shipments",
        default=0,
    )
    out_shipment_count = fields.Integer(
        compute=_compute_out_shipment_count,
        string="# of Deliveries",
        default=0,
    )
    move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="rma_line_id",
        string="Stock Moves",
        readonly=True,
        copy=False)
    reference_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Originating stock move",
        readonly=True,
        copy=False,
    )
    # procurement_ids = fields.One2many(
    #     comodel_name="procurement.order",
    #     inverse_name="rma_line_id",
    #     string="Procurements",
    #     readonly=True,
    #     states={
    #         "draft": [
    #             ("readonly", False),
    #         ],
    #     },
    #     copy=False,
    # )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="rma_id.company_id",
        store=True,
    )
    type = fields.Selection(
        related="rma_id.type",
    )
    customer_to_supplier = fields.Boolean(
        string="The customer will send to the supplier",
    )
    supplier_to_customer = fields.Boolean(
        string="The supplier will send to the customer",
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
        default=lambda self: self._default_rma_supplier_policy(),
    )
    allowed_route_template_ids = fields.Many2many(
        string="Allowed Route Template",
        comodel_name="rma.route_template",
        compute="_compute_allowed_route_template_ids",
        store=False,
    )
    route_template_id = fields.Many2one(
        string="Route Template",
        comodel_name="rma.route_template",
    )
    in_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Inbound Route",
        required=False,
        domain=[
            ("rma_selectable", "=", True),
        ],
    )
    out_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Outbound Route",
        required=False,
        domain=[
            ("rma_selectable", "=", True),
        ],
    )
    in_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Inbound Warehouse",
        required=False,
        default=lambda self: self._default_warehouse_id(),
    )
    out_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Outbound Warehouse",
        required=False,
        default=lambda self: self._default_warehouse_id(),
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Send To This Company Location",
        required=False,
        default=lambda self: self._default_location_id(),
    )
    customer_rma_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="Customer RMA line",
        ondelete="cascade",
    )
    supplier_rma_line_ids = fields.One2many(
        comodel_name="rma.order.line",
        inverse_name="customer_rma_id",
    )
    supplier_address_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        string="Supplier Address",
        help="This address of the supplier in case of Customer RMA operation "
             "dropship.",
    )
    qty_to_receive = fields.Float(
        string="Qty To Receive",
        digits=dp.get_precision("Product Unit of Measure"),
        compute=_compute_qty_to_receive,
        store=True,
    )
    qty_incoming = fields.Float(
        string="Incoming Qty",
        copy=False,
        readonly=True,
        digits=dp.get_precision("Product Unit of Measure"),
        compute=_compute_qty_incoming,
        store=True,
    )
    qty_received = fields.Float(
        string="Qty Received",
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        compute=_compute_qty_received,
        store=True,
    )
    qty_to_deliver = fields.Float(
        string="Qty To Deliver", copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        compute=_compute_qty_to_deliver,
        store=True,
    )
    qty_outgoing = fields.Float(
        string="Outgoing Qty",
        copy=False,
        readonly=True,
        digits=dp.get_precision("Product Unit of Measure"),
        compute=_compute_qty_outgoing,
        store=True,
    )
    qty_delivered = fields.Float(
        string="Qty Delivered",
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        compute=_compute_qty_delivered,
        store=True,
    )
    qty_to_supplier_rma = fields.Float(
        string="Qty to send to Supplier RMA",
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        compute=_compute_qty_supplier_rma,
        store=True,
    )
    qty_in_supplier_rma = fields.Float(
        string="Qty in Supplier RMA",
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True, compute=_compute_qty_in_supplier_rma,
        store=True,
    )

    @api.model
    def _create_sequence(self, values):
        obj_sequence = self.env["ir.sequence"]
        if self.env.context.get("supplier"):
            name = obj_sequence.next_by_code(
                "rma.order.line.supplier")
        else:
            name = obj_sequence.next_by_code(
                "rma.order.line.customer")
        return name

    @api.model
    def _prepare_create_data(self, values):
        name = values.get("name", False)
        if not name or name == "/":
            values["name"] = self._create_sequence(values)
        return values

    @api.model
    def create(self, vals):
        new_values = self._prepare_create_data(vals)
        return super(RmaOrderLine, self).create(new_values)

    @api.onchange(
        "operation_id",
    )
    def onchange_receipt_policy_id(self):
        if self.operation_id:
            self.receipt_policy_id = self.operation_id.receipt_policy_id

    @api.onchange(
        "operation_id",
    )
    def onchange_delivery_policy_id(self):
        if self.operation_id:
            self.delivery_policy_id = self.operation_id.delivery_policy_id

    @api.onchange(
        "route_template_id",
    )
    def onchange_in_warehouse_id(self):
        if self.route_template_id:
            self.in_warehouse_id = self.route_template_id.in_warehouse_id

    @api.onchange(
        "route_template_id",
    )
    def onchange_out_warehouse_id(self):
        if self.route_template_id:
            self.out_warehouse_id = self.route_template_id.out_warehouse_id

    @api.onchange(
        "route_template_id",
    )
    def onchange_location_id(self):
        if self.route_template_id:
            self.location_id = self.route_template_id.location_id or \
                self.in_warehouse_id.lot_rma_id

    @api.onchange(
        "route_template_id",
    )
    def onchange_customer_to_supplier(self):
        if self.route_template_id:
            self.customer_to_supplier = self.route_template_id.\
                customer_to_supplier

    @api.onchange(
        "route_template_id",
    )
    def onchange_supplier_to_customer(self):
        if self.route_template_id:
            self.supplier_to_customer = self.route_template_id.\
                supplier_to_customer

    @api.onchange(
        "route_template_id",
    )
    def onchange_in_route_id(self):
        if self.route_template_id:
            self.in_route_id = self.route_template_id.in_route_id

    @api.onchange(
        "route_template_id",
    )
    def onchange_out_route_id(self):
        if self.route_template_id:
            self.out_route_id = self.route_template_id.out_route_id

    @api.onchange(
        "operation_id",
    )
    def onchange_route_template(self):
        self.route_template_id = False
        if self.operation_id and self.operation_id.default_route_template_id:
            self.route_template_id = self.operation_id.\
                default_route_template_id

    @api.onchange("customer_to_supplier", "type")
    def _onchange_receipt_policy(self):
        if self.type == "supplier" and self.customer_to_supplier:
            self.receipt_policy = "no"
        elif self.type == "customer" and self.supplier_to_customer:
            self.delivery_policy = "no"

    @api.onchange(
        "product_id",
    )
    def _onchange_product_id(self):
        self.product_qty = 1
        if self.product_id:
            if self.lot_id.product_id != self.product_id:
                self.lot_id = False
            self.price_unit = self.product_id.standard_price
            product_tmpl = self.product_id.product_tmpl_id
            if not self.operation_id:
                self.operation_id = product_tmpl._get_rma_operation(
                    self.type)
            self.uom_id = self.product_id.uom_id
            return {"domain": {
                "lot_id": [("product_id", "=", self.product_id.id)]}}
        return {"domain": {"lot_id": []}}

    @api.onchange(
        "lot_id",
    )
    def _onchange_lot_id(self):
        product = self.lot_id.product_id
        if product:
            self.product_id = product
            self.uom_id = product.uom_id

    @api.multi
    def action_view_in_shipments(self):
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        picking_ids = []
        suppliers = self.env.ref("stock.stock_location_suppliers")
        customers = self.env.ref("stock.stock_location_customers")
        for line in self:
            if line.type == "customer":
                for move in line.move_ids:
                    if move.picking_id.location_id == customers:
                        picking_ids.append(move.picking_id.id)
            else:
                for move in line.move_ids:
                    if move.picking_id.location_id == suppliers:
                        picking_ids.append(move.picking_id.id)
        shipments = list(set(picking_ids))
        # choose the view_mode accordingly
        if len(shipments) != 1:
            result["domain"] = "[('id', 'in', " + \
                               str(shipments) + ")]"
        elif len(shipments) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = shipments[0]
        return result

    @api.multi
    def action_view_out_shipments(self):
        action = self.env.ref("stock.action_picking_tree_all")
        result = action.read()[0]
        picking_ids = []
        suppliers = self.env.ref("stock.stock_location_suppliers")
        customers = self.env.ref("stock.stock_location_customers")
        for line in self:
            if line.type == "customer":
                for move in line.move_ids:
                    if move.picking_id.location_id != customers:
                        picking_ids.append(move.picking_id.id)
            else:
                for move in line.move_ids:
                    if move.picking_id.location_id != suppliers:
                        picking_ids.append(move.picking_id.id)
        shipments = list(set(picking_ids))
        # choose the view_mode accordingly
        if len(shipments) != 1:
            result["domain"] = "[('id', 'in', " + \
                               str(shipments) + ")]"
        elif len(shipments) == 1:
            res = self.env.ref("stock.view_picking_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = shipments[0]
        return result

    # @api.multi
    # def action_view_procurements(self):
    #     action = self.env.ref(
    #         "procurement.procurement_exceptions")
    #     result = action.read()[0]
    #     procurements = self.procurement_ids.filtered(
    #         lambda p: p.state == "exception").ids
    #     # choose the view_mode accordingly
    #     if len(procurements) != 1:
    #         result["domain"] = "[('id', 'in', " + \
    #                            str(procurements) + ")]"
    #     elif len(procurements) == 1:
    #         res = self.env.ref("procurement.procurement_form_view", False)
    #         result["views"] = [(res and res.id or False, "form")]
    #         result["res_id"] = procurements[0]
    #     return result
