# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.one
    def _compute_rma_count(self):
        rma_list = []
        for invl in self.invoice_line:
            for rmal in invl.rma_line_ids:
                rma_list.append(rmal.rma_id.id)
        self.rma_count = len(list(set(rma_list)))

    rma_count = fields.Integer(
        compute=_compute_rma_count,
        string="# of RMA",
        copy=False,
    )

    @api.multi
    def action_view_rma_supplier(self):
        action = self.env.ref("rma.action_rma_supplier")
        result = action.read()[0]
        rma_list = []
        for invl in self.invoice_line_ids:
            for rmal in invl.rma_line_ids:
                rma_list.append(rmal.rma_id.id)
        self.rma_count = len(list(set(rma_list)))
        # choose the view_mode accordingly
        if len(rma_list) != 1:
            result["domain"] = "[('id', 'in', " + \
                               str(rma_list) + ")]"
        elif len(rma_list) == 1:
            res = self.env.ref("rma.view_rma_supplier_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = rma_list[0]
        return result

    @api.multi
    def action_view_rma(self):
        action = self.env.ref("rma.action_rma_customer")
        result = action.read()[0]
        rma_list = []
        for invl in self.invoice_line_ids:
            for rmal in invl.rma_line_ids:
                rma_list.append(rmal.rma_id.id)
        self.rma_count = len(list(set(rma_list)))
        # choose the view_mode accordingly
        if len(rma_list) != 1:
            result["domain"] = "[('id', 'in', " + \
                               str(rma_list) + ")]"
        elif len(rma_list) == 1:
            res = self.env.ref("rma.view_rma_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = rma_list[0]
        return result


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    @api.multi
    def _compute_rma_count(self):
        rma_list = []
        for invl in self:
            for rmal in invl.rma_line_ids:
                rma_list.append(rmal.rma_id.id)
            invl.rma_count = len(list(set(rma_list)))

    rma_count = fields.Integer(
        compute=_compute_rma_count,
        string="# of RMA",
        copy=False,
    )
    rma_line_ids = fields.One2many(
        comodel_name="rma.order.line",
        inverse_name="invoice_line_id",
        string="RMA",
        readonly=True,
        help="This will contain the RMA lines for the invoice line",
    )
    rma_line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA line refund",
        ondelete="set null",
        help="This will contain the rma line that originated the refund line",
    )

    @api.multi
    def _prepare_rma_line_from_inv_line(self):
        operation = self.product_id.product_tmpl_id._get_rma_operation(
            self.rma_id.type)
        data = {
            "invoice_line_id": self.id,
            "product_id": self.product_id.id,
            "name": self.name,
            "origin": self.invoice_id.number,
            "uom_id": self.uos_id.id,
            "operation_id": operation,
            "product_qty": self.quantity,
            "price_unit": self.price_unit,
            # "price_unit": self.invoice_id.currency_id.compute(
            #     line.price_unit, line.currency_id, round=False),
        }
        return data
