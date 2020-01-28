# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RmaAddinvoice(models.TransientModel):
    _name = "rma_add_invoice"
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
        string="RMA Order",
        comodel_name="rma.order",
        readonly=False,
        ondelete="cascade",
        default=lambda self: self._default_rma_id(),
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        readonly=True,
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
    invoice_id = fields.Many2one(
        string="Invoice",
        comodel_name="account.invoice",
    )
    invoice_line_ids = fields.Many2many(
        string="Invoice Lines",
        comodel_name="account.invoice.line",
        relation="rma_add_invoice_add_line_rel",
        column1="invoice_line_id",
        column2="rma_add_invoice_id",
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
            "delivery_address_id": self.invoice_id.partner_id.id,
            "invoice_address_id": self.invoice_id.partner_id.id
        }
        return data

    @api.model
    def _get_existing_invoice_lines(self):
        existing_invoice_lines = []
        for rma_line in self.rma_id.rma_line_ids:
            existing_invoice_lines.append(rma_line.invoice_line_id)
        return existing_invoice_lines

    @api.multi
    def add_lines(self):
        self.ensure_one()
        existing_invoice_lines = self._get_existing_invoice_lines()
        for line in self.invoice_line_ids:
            if line not in existing_invoice_lines:
                line._create_rma_line(
                    rma=self.rma_id, operation=self.operation_id,
                    route_template=self.route_template_id)
        rma = self.rma_id
        data_rma = self._get_rma_data()
        rma.write(data_rma)
        return {"type": "ir.actions.act_window_close"}
