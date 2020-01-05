# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class RmaAddPurchase(models.TransientModel):
    _name = "rma_add_purchase"
    _description = "Wizard to add rma lines"

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
        ondelete="cascade",
        default=lambda self: self._default_rma_id(),
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=False,
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Order",
    )
    operation_id = fields.Many2one(
        string="Operation",
        comodel_name="rma.operation",
        domain=[("type", "=", "supplier")],
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
    purchase_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="rma_add_purchase_add_line_rel",
        column1="purchase_line_id",
        column2="rma_add_purchase_id",
        readonly=False,
        string="Purcahse Order Lines",
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
    def _get_rma_data(self):
        data = {
            "date_rma": fields.Datetime.now(),
            "delivery_address_id": self.purchase_id.partner_id.id,
            "invoice_address_id": self.purchase_id.partner_id.id
        }
        return data

    @api.multi
    def add_lines(self):
        self.ensure_one()
        rma = self.rma_id
        existing_purchase_lines = rma._get_existing_purchase_lines()
        for line in self.purchase_line_ids:
            if line not in existing_purchase_lines:
                line._create_rma_line_from_po_line(
                    rma=rma,
                    operation=self.operation_id,
                    route_template=self.route_template_id)
        data_rma = self._get_rma_data()
        rma.write(data_rma)
        return {"type": "ir.actions.act_window_close"}
