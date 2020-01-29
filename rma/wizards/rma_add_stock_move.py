# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class RmaAddStockMove(models.TransientModel):
    _name = "rma_add_stock_move"
    _description = "Wizard to add rma lines from pickings"

    @api.model
    def _default_rma_id(self):
        return self.env.context.get("active_id", False)

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

    rma_id = fields.Many2one(
        comodel_name="rma.order",
        string="RMA Order",
        readonly=False,
        default=lambda self: self._default_rma_id(),
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=False,
    )
    operation_id = fields.Many2one(
        string="RMA Operation",
        comodel_name="rma.operation",
    )
    allowed_route_template_ids = fields.Many2many(
        string="Allowed Route Template",
        comodel_name="rma.route_template",
        compute="_compute_allowed_route_template_ids",
        store=False,
    )
    route_template_id = fields.Many2one(
        string="RMA Route Template",
        comodel_name="rma.route_template",
    )
    move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Stock Moves",
        domain="[('state', '=', 'done')]",
    )

    @api.onchange(
        "rma_id",
    )
    def onchange_partner_id(self):
        self.partner_id = False
        if self.rma_id:
            self.partner_id = self.rma_id.partner_id

    @api.onchange(
        "operation_id",
    )
    def onchange_route_template(self):
        self.route_template_id = False
        if self.operation_id and self.operation_id.default_route_template_id:
            self.route_template_id = self.operation_id.\
                default_route_template_id

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
                sm._create_rma_line(
                    rma=self.rma_id,
                    operation=self.operation_id,
                    route_template=self.route_template_id)
        return {"type": "ir.actions.act_window_close"}
