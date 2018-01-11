# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class RmaOrderLine(models.Model):
    _inherit = "rma.order.line"

    @api.model
    def _default_repair_policy(self):
        return self.env.ref("rma.rma_policy_no") or False

    @api.multi
    @api.depends(
        "receipt_policy_id", "delivery_policy_id",
        "rma_supplier_policy_id", "repair_policy_id",
        "refund_policy_id", "type",
        "product_qty", "qty_received",
        "qty_delivered", "qty_in_supplier_rma",
        "qty_refunded", "qty_repaired",
    )

    def _compute_qty_to_repair(self):
        for rec in self:
            rec.qty_to_repair = rec.refund_policy_id._compute_quantity(rec)

    @api.multi
    @api.depends('repair_ids', 'repair_ids.state',
                 'qty_to_receive')
    def _compute_qty_repaired(self):
        for rec in self:
            rec.qty_repaired = rec._get_rma_repaired_qty()

    @api.multi
    def _compute_repair_count(self):
        for line in self:
            line.repair_count = len(line.repair_ids)

    repair_ids = fields.One2many(
        comodel_name='mrp.repair', inverse_name='rma_line_id',
        string='Repair Orders', readonly=True,
        states={'draft': [('readonly', False)]}, copy=False)
    qty_to_repair = fields.Float(
        string='Qty To Repair', copy=False,
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute=_compute_qty_to_repair,
        store=True)
    qty_repaired = fields.Float(
        string='Qty Repaired', copy=False,
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute=_compute_qty_repaired,
        store=True, help="Quantity repaired or being repaired.")
    repair_policy_id = fields.Many2one(
        string="Repair Policy",
        comodel_name="rma.policy",
        domain=[
            ("rma_type", "in", ["both", "customer"]),
            ("repair_policy_ok", "=", True),
            ],
        required=True,
        default=lambda self: self._default_repair_policy(),
        )
    repair_count = fields.Integer(
        compute=_compute_repair_count, string='# of Repairs')

    @api.multi
    def action_view_repair_order(self):
        action = self.env.ref('mrp_repair.action_repair_order_tree')
        result = action.read()[0]
        result['domain'] = [('id', 'in', self.repair_ids.ids)]
        return result

    @api.multi
    def _get_rma_repaired_qty(self):
        self.ensure_one()
        qty = 0.0
        for repair in self.repair_ids.filtered(
                lambda p: p.state != 'cancel'):
            repair_qty = self.env['product.uom']._compute_qty_obj(
                self.uom_id,
                repair.product_qty,
                repair.product_uom,
            )
            qty += repair_qty
        return qty
