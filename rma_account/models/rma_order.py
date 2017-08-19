# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class RmaOrder(models.Model):
    _inherit = "rma.order"

    @api.multi
    def _compute_invoice_refund_count(self):
        self.ensure_one()
        invoice_list = []
        for line in self.rma_line_ids:
            for refund in line.refund_line_ids:
                if refund.invoice_id:
                    invoice_list.append(refund.invoice_id.id)
        self.invoice_refund_count = len(list(set(invoice_list)))

    @api.multi
    def _compute_invoice_count(self):
        self.ensure_one()
        invoice_list = []
        for line in self.rma_line_ids:
            if line.invoice_line_id:
                invoice_list.append(line.invoice_line_id.invoice_id.id)
        self.invoice_count = len(list(set(invoice_list)))

    add_invoice_id = fields.Many2one(
        comodel_name="account.invoice",
        string="Add Invoice",
        ondelete="set null",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    invoice_refund_count = fields.Integer(
        compute="_compute_invoice_refund_count",
        string="# of Refunds",
        copy=False,
    )
    invoice_count = fields.Integer(
        compute="_compute_invoice_count",
        string="# of Incoming Shipments",
        copy=False,
    )

    @api.onchange("add_invoice_id")
    def on_change_invoice(self):
        if not self.add_invoice_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.add_invoice_id.partner_id.id
        new_lines = self.env["rma.order.line"]
        for line in self.add_invoice_id.invoice_line_ids:
            # Load a PO line only once
            if line in self.rma_line_ids.mapped("invoice_line_id"):
                continue
            data = self._prepare_rma_line_from_inv_line(line)
            new_line = new_lines.new(data)
            new_lines += new_line

        self.rma_line_ids += new_lines
        self.date_rma = fields.Datetime.now()
        self.delivery_address_id = self.add_invoice_id.partner_id.id
        self.invoice_address_id = self.add_invoice_id.partner_id.id
        self.add_invoice_id = False
        return {}

    @api.multi
    def action_view_invoice_refund(self):
        """
        This function returns an action that display existing vendor refund
        bills of given purchase order id.
        When only one found, show the vendor bill immediately.
        """
        action = self.env.ref("account.action_invoice_tree2")
        result = action.read()[0]
        invoice_list = []
        for line in self.rma_line_ids:
            for refund in line.refund_line_ids:
                invoice_list.append(refund.invoice_id.id)
        invoice_ids = list(set(invoice_list))
        # choose the view_mode accordingly
        if len(invoice_ids) != 1:
            result["domain"] = "[('id', 'in', " + \
                               str(invoice_ids) + ")]"
        elif len(invoice_ids) == 1:
            res = self.env.ref("account.invoice_supplier_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = invoice_ids[0]
        return result

    @api.multi
    def action_view_invoice(self):
        if self.type == "supplier":
            action = self.env.ref("account.action_invoice_tree2")
        else:
            action = self.env.ref("account.action_invoice_tree")
        result = action.read()[0]
        invoice_list = []
        for line in self.rma_line_ids:
            invoice_list.append(line.invoice_id.id)
        invoice_ids = list(set(invoice_list))
        # choose the view_mode accordingly
        if len(invoice_ids) != 1:
            result["domain"] = "[('id', 'in', " + \
                               str(invoice_ids) + ")]"
        elif len(invoice_ids) == 1:
            if self.type == "supplier":
                res = self.env.ref("account.invoice_supplier_form", False)
            else:
                res = self.env.ref("account.invoice_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = invoice_ids[0]
        return result
