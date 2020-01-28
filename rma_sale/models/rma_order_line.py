# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class RmaOrderLine(models.Model):
    _inherit = "rma.order.line"

    @api.model
    def _default_sale_policy(self):
        try:
            result = self.env.ref("rma.rma_policy_no")
        except ValueError:
            result = self.env["rma.policy"]._create_default_policy()
        return result

    @api.multi
    @api.depends(
        "sale_line_ids",
        "sales_count",
        "sale_line_ids.state",
    )
    def _compute_qty_sold(self):
        for line in self:
            line.qty_sold = line._get_rma_sold_qty()

    @api.multi
    @api.depends(
        "receipt_policy_id", "delivery_policy_id", "sale_policy_id",
        "rma_supplier_policy_id", "refund_policy_id", "type",
        "product_qty", "qty_received",
        "qty_delivered", "qty_in_supplier_rma", "qty_refunded",
        "qty_sold",
    )
    def _compute_qty_to_sell(self):
        for rec in self:
            rec.qty_to_sell = rec.sale_policy_id._compute_quantity(rec)

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
    sale_policy_id = fields.Many2one(
        string="Sale Policy",
        comodel_name="rma.policy",
        domain=[
            ("rma_type", "=", "both"),
            ("sale_policy_ok", "=", True),
        ],
        required=True,
        default=lambda self: self._default_sale_policy(),
    )
    sales_count = fields.Integer(
        compute=_compute_sales_count,
        string="# of Sales",
        copy=False,
        default=0,
    )

    @api.onchange(
        "operation_id",
    )
    def onchange_sale_policy_id(self):
        if self.operation_id:
            self.sale_policy_id = self.operation_id.sale_policy_id

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
