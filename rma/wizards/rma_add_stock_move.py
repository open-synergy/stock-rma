# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class RmaAddStockMove(models.TransientModel):
    _name = "rma_add_stock_move"
    _description = "Wizard to add rma lines from pickings"

    @api.model
    def default_get(self, fields):
        res = super(RmaAddStockMove, self).default_get(fields)
        rma_obj = self.env["rma.order"]
        rma_id = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_id:
            return res
        assert active_model == "rma.order", "Bad context propagation"

        rma = rma_obj.browse(rma_id)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
        res["picking_id"] = False
        res["move_ids"] = False
        return res

    rma_id = fields.Many2one(
        comodel_name="rma.order",
        string="RMA Order",
        readonly=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=True,
    )
    move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Stock Moves",
        domain="[('state', '=', 'done')]",
    )

    @api.model
    def _get_existing_stock_moves(self):
        existing_move_lines = []
        for rma_line in self.rma_id.rma_line_ids:
            existing_move_lines.append(rma_line.reference_move_id)
        return existing_move_lines

    @api.multi
    def add_lines(self):
        self.ensure_one()
        existing_stock_moves = self._get_existing_stock_moves()
        for sm in self.move_ids:
            if sm not in existing_stock_moves:
                sm._create_rma_line(self.rma_id)
        return {"type": "ir.actions.act_window_close"}
