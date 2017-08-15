# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class RmaOrderLine(models.Model):
    _inherit = "rma.order.line"

    @api.model
    def _default_sale_type(self):
        return self.sale_type or False

    sale_type = fields.Selection(
        selection=[
            ("no", "Not required"),
            ("ordered", "Based on Ordered Quantities"),
            ("received", "Based on Received Quantities"),
        ],
        string="Sale Policy",
        default=lambda self: self._default_sale_type(),
    )

    @api.multi
    @api.depends(
        "sale_line_ids",
        "sale_type",
        "sales_count",
        "sale_line_ids.state",
    )
    def _compute_qty_to_sell(self):
        for line in self:
            if line.sale_type == "no":
                line.qty_to_sell = 0.0
            elif line.sale_type == "ordered":
                qty = line._get_rma_sold_qty()
                line.qty_to_sell = line.product_qty - qty
            elif line.sale_type == "received":
                qty = line._get_rma_sold_qty()
                line.qty_to_sell = line.qty_received - qty
            else:
                line.qty_to_sell = 0.0

    @api.multi
    @api.depends(
        "sale_line_ids",
        "sale_type",
        "sales_count",
        "sale_line_ids.state",
    )
    def _compute_qty_sold(self):
        for line in self:
            line.qty_sold = line._get_rma_sold_qty()

    @api.multi
    @api.depends(
        "sale_line_ids",
    )
    def _compute_sales_count(self):
        for line in self:
            sales_list = []
            for sale_order_line in line.sale_line_ids:
                sales_list.append(sale_order_line.order_id.id)
            line.sales_count = len(list(set(sales_list)))

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Originating Sales Order Line",
        ondelete="restrict",
    )
    sale_line_ids = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="rma_line_id",
        string="Sales Order Lines",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        copy=False,
    )
    qty_to_sell = fields.Float(
        string="Qty To Sell",
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        compute=_compute_qty_to_sell,
        store=True,
    )
    qty_sold = fields.Float(
        string="Qty Sold",
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        compute=_compute_qty_sold,
        store=True,
    )
    sale_type = fields.Selection(
        selection=[
            ("no", "Not required"),
            ("ordered", "Based on Ordered Quantities"),
            ("received", "Based on Received Quantities"),
        ],
        string="Sale Policy",
        default="no",
        required=True,
    )
    sales_count = fields.Integer(
        compute=_compute_sales_count,
        string="# of Sales",
        copy=False,
        default=0,
    )

    @api.multi
    def action_view_sale_order(self):
        # TODO: Review
        action = self.env.ref("sale.action_quotations")
        result = action.read()[0]
        order_ids = []
        for sale_line in self.sale_line_ids:
            order_ids.append(sale_line.order_id.id)
        result["domain"] = [("id", "in", order_ids)]
        return result

    @api.multi
    def _get_rma_sold_qty(self):
        self.ensure_one()
        qty = 0.0
        for sale_line in self.sale_line_ids.filtered(
                lambda p: p.state not in ("draft", "sent", "cancel")):
            qty += sale_line.product_uom_qty
        return qty
