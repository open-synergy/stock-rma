# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT
import openerp.addons.decimal_precision as dp


class RmaMakePicking(models.TransientModel):
    _name = "rma_make_picking.wizard"
    _description = "Wizard to create pickings from rma lines"

    @api.returns("rma.order.line")
    def _prepare_item(self, line):
        values = {"product_id": line.product_id.id,
                  "product_qty": line.product_qty,
                  "uom_id": line.uom_id.id,
                  "qty_to_receive": line.qty_to_receive,
                  "qty_to_deliver": line.qty_to_deliver,
                  "line_id": line.id,
                  "rma_id": line.rma_id.id,
                  }
        return values

    @api.model
    def default_get(self, fields):
        """Default values for wizard, if there is more than one supplier on
        lines the supplier field is empty otherwise is the unique line
        supplier.
        """
        res = super(RmaMakePicking, self).default_get(fields)
        rma_line_obj = self.env["rma.order.line"]
        rma_line_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]

        if not rma_line_ids:
            return res
        assert active_model == "rma.order.line", \
            "Bad context propagation"

        items = []
        lines = rma_line_obj.browse(rma_line_ids)
        if len(lines.mapped("partner_id")) > 1:
            raise ValidationError(
                _("Only RMA lines from the same partner can be processed at "
                  "the same time"))
        for line in lines:
            items.append([0, 0, self._prepare_item(line)])
        res["item_ids"] = items
        return res

    @api.model
    def _default_picking_type(self):
        return self.env.context.get("picking_type", "incoming")

    item_ids = fields.One2many(
        comodel_name="rma_make_picking.wizard.item",
        inverse_name="wiz_id",
        string="Items",
    )
    picking_type = fields.Selection(
        string="Picking Type",
        selection=[
            ("incoming", "Incoming"),
            ("outgoing", "Outgoing"),
        ],
        default=lambda self: self._default_picking_type(),
    )

    @api.model
    def _get_action(self, pickings, procurements):
        if pickings:
            action = procurements.do_view_pickings()
        else:
            action = self.env.ref(
                "procurement.procurement_exceptions")
            action = action.read()[0]
            # choose the view_mode accordingly
            procurement_ids = procurements.ids
            if len(procurement_ids) != 1:
                action["domain"] = "[('id', 'in', " + \
                                   str(procurement_ids) + ")]"
            elif len(procurements) == 1:
                res = self.env.ref("procurement.procurement_form_view",
                                   False)
                action["views"] = [(res and res.id or False, "form")]
                action["res_id"] = procurement_ids[0]
        return action

    @api.multi
    def action_create_picking(self):
        self.ensure_one()
        procurements = self.env["procurement.order"]
        for item in self.item_ids:
            procurements += item._create_procurement()
        procurements.run()
        groups = []
        for proc in procurements:
            if proc.group_id:
                groups.append(proc.group_id.id)
        if len(groups):
            pickings = self.env["stock.picking"].search(
                [("group_id", "in", groups)])

        action = self._get_action(pickings, procurements)
        return action

    @api.multi
    def action_cancel(self):
        return {"type": "ir.actions.act_window_close"}


class RmaMakePickingItem(models.TransientModel):
    _name = "rma_make_picking.wizard.item"
    _description = "Items to receive"

    @api.multi
    @api.depends(
        "wiz_id.picking_type",
        "qty_to_receive",
        "qty_to_deliver",
    )
    def _compute_qty(self):
        for item in self:
            if item.wiz_id.picking_type == "incoming":
                item.qty = item.qty_to_receive
            else:
                item.qty = item.qty_to_deliver

    @api.multi
    @api.depends(
        "line_id",
    )
    def _compute_delivery_address_id(self):
        for item in self:
            item.delivery_address_id = False
            if item.line_id.delivery_address_id:
                item.delivery_address_id = item.line_id.delivery_address_id
            elif item.line_id.customer_to_supplier:
                item.delivery_address_id = item.line_id.supplier_address_id
            elif item.line_id.partner_id:
                item.delivery_address_id = item.line_id.partner_id

    @api.multi
    @api.depends(
        "wiz_id.picking_type",
        "line_id",
        "delivery_address_id",
    )
    def _compute_data(self):
        for item in self:
            picking_type = item.wiz_id.picking_type
            line = item.line_id
            delivery = item.delivery_address_id
            if picking_type == "incoming":
                if line.customer_to_supplier:
                    item.location_id = delivery.property_stock_supplier
                else:
                    item.location_id = line.location_id
                item.warehouse_id = line.in_warehouse_id
                item.route_id = line.in_route_id
            else:
                if line.rma_id.type == "customer":
                    item.location_id = delivery.property_stock_customer
                else:
                    item.location_id = delivery.property_stock_supplier
                item.warehouse_id = line.out_warehouse_id
                item.route_id = line.out_route_id

    wiz_id = fields.Many2one(
        comodel_name="rma_make_picking.wizard",
        string="Wizard",
        required=False,
    )
    line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA order Line",
        readonly=True,
        ondelete="cascade",
    )
    rma_id = fields.Many2one(
        comodel_name="rma.order",
        related="line_id.rma_id",
        string="RMA",
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        readonly=True,
    )
    product_qty = fields.Float(
        related="line_id.product_qty",
        string="Quantity Ordered",
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
    )
    qty_to_receive = fields.Float(
        string="Quantity to Receive",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    qty_to_deliver = fields.Float(
        string="Quantity To Deliver",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    qty = fields.Float(
        string="Quantity To Deliver",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_qty",
    )
    uom_id = fields.Many2one(
        "product.uom",
        string="Unit of Measure",
        readonly=True,
    )
    delivery_address_id = fields.Many2one(
        string="Delivery Address",
        comodel_name="res.partner",
        compute="_compute_delivery_address_id",
        store=False,
    )
    location_id = fields.Many2one(
        string="Location",
        comodel_name="stock.location",
        compute="_compute_data",
        store=False,
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        compute="_compute_data",
        store=False,
    )
    route_id = fields.Many2one(
        string="Route",
        comodel_name="stock.location.route",
        compute="_compute_data",
        store=False,
    )

    @api.multi
    def find_procurement_group(self, item):
        self.ensure_one()
        return self.env["procurement.group"].search([("rma_id", "=",
                                                      self.line_id.rma_id.id)])

    @api.multi
    def _prepare_procurement_group_data(self):
        group_data = {
            "name": self.line_id.rma_id.name,
            "rma_id": self.line_id.rma_id.id,
        }
        return group_data

    @api.multi
    def _get_procurement_group(self):
        group = self.find_procurement_group(self)
        if not group:
            group_data = self._prepare_procurement_group_data()
            group = self.env["procurement.group"].create(
                group_data)
        return group

    @api.model
    def _create_procurement(self):
        procurement_data = self._prepare_procurement_data()
        # create picking
        procurement = self.env["procurement.order"].create(procurement_data)
        return procurement

    @api.multi
    def _prepare_procurement_data(self):
        self.ensure_one()
        line = self.line_id
        group = self._get_procurement_group()
        wh = self.warehouse_id
        delivery = self.delivery_address_id
        procurement_data = {
            "name": line.rma_id.name,
            "group_id": group.id,
            "origin": line.rma_id.name,
            "warehouse_id": wh and wh.id or False,
            "date_planned": time.strftime(DT_FORMAT),
            "product_id": self.product_id.id,
            "product_qty": self.qty,
            "partner_dest_id": delivery and delivery.id or False,
            "product_uom": line.product_id.product_tmpl_id.uom_id.id,
            "location_id": self.location_id and self.location_id.id or False,
            "rma_line_id": line.id,
        }
        if self.route_id:
            procurement_data.update({
                "route_ids": [(4, self.route_id.id)]})
        return procurement_data
