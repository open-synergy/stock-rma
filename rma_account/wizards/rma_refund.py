# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class RmaRefund(models.TransientModel):
    _name = "rma.refund"

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_ids = context.get("active_ids", False)
        if active_ids:
            rma_lines = self.env["rma.order.line"].browse(active_ids[0])
            return rma_lines.rma_id.name
        return ""

    @api.returns("rma.order.line")
    def _prepare_item(self, line):
        values = {"product_id": line.product_id.id,
                  "name": line.product_id.display_name,
                  "product_qty": line.product_qty,
                  "uom_id": line.uom_id.id,
                  "qty_to_refund": line.qty_to_refund,
                  "refund_policy": line.refund_policy,
                  "invoice_address_id": line.invoice_address_id.id,
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
        res = super(RmaRefund, self).default_get(
            fields)
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
            raise UserError(
                _("Only RMA lines from the same partner can be processed at "
                  "the same time"))
        for line in lines:
            items.append([0, 0, self._prepare_item(line)])
        res["item_ids"] = items
        return res

    date_invoice = fields.Date(
        string="Refund Date",
        default=fields.Date.context_today,
        required=True,
    )
    description = fields.Char(
        string="Reason",
        required=True,
        default=lambda self: self._get_reason(),
    )
    item_ids = fields.One2many(
        comodel_name="rma.refund.item",
        inverse_name="wiz_id",
        string="Items",
    )

    @api.multi
    def compute_refund(self):
        for wizard in self:
            first = self.item_ids[0]
            values = self._prepare_refund(first.rma_id)
            if len(first.line_id.invoice_address_id):
                values["partner_id"] = first.line_id.invoice_address_id.id
            else:
                values["partner_id"] = first.rma_id.partner_id.id
            new_refund = self.env["account.invoice"].create(values)
            # Put the reason in the chatter
            subject = _("Invoice refund")
            body = self.item_ids[0].rma_id.name
            new_refund.message_post(body=body, subject=subject)
            return new_refund

    @api.multi
    def invoice_refund(self):
        rma_line_ids = self.env["rma.order.line"].browse(
            self.env.context["active_ids"])
        # TODO: Create method
        for line in rma_line_ids:
            if line.refund_policy == "no":
                raise UserError(
                    _("The operation is not refund for at least one line"))
            if line.state != "approved":
                raise UserError(
                    _("RMA %s is not approved") %
                    line.rma_id.name)
        new_invoice = self.compute_refund()
        action = "action_invoice_tree1" if (
            new_invoice.type in ["out_refund", "out_invoice"]) \
            else "action_invoice_tree2"
        result = self.env.ref("account.%s" % action).read()[0]
        invoice_domain = eval(result["domain"])
        invoice_domain.append(("id", "=", new_invoice.id))
        result["domain"] = invoice_domain
        return result

    @api.model
    def _get_journal(self, order):
        obj_journal = self.env["account.journal"]
        if order.type == "customer":
            domain = [("type", "=", "sale_refund")]
        else:
            domain = [("type", "=", "purchase_refund")]
        journal = obj_journal.search(domain, limit=1)
        if not journal:
            raise UserError(_("No journal defined"))
        return journal

    @api.model
    def _get_period(self, date_invoice):
        obj_period = self.env["account.period"]
        return obj_period.find(date_invoice)

    @api.multi
    def _prepare_refund(self, order):
        self.ensure_one()
        # origin_invoices = self._get_invoice(order)
        date_invoice = self.date_invoice or fields.Date.context.today
        partner = order.partner_id
        commercial_partner = partner.commercial_partner_id
        lines = []
        journal = self._get_journal(order)
        values = {
            "name": order.name,
            "origin": order.name,
            "reference": False,
            "date_invoice": date_invoice,
            "period_id": self._get_period(date_invoice).id,
            "account_id": commercial_partner.property_account_receivable.id,
            "journal_id": journal.id,
            "type": order.type == "customer" and "out_refund" or "in_refund",
            "partner_id": partner.id,
            "currency_id": self.env.user.company_id.currency_id.id,
            "payment_term_id": False,
            "fiscal_position_id":
                partner.property_account_position.id,
        }
        for line in self.item_ids:
            lines.append((0, 0,
                          line._prepare_refund_line()))
        values["invoice_line"] = lines

        return values

    @api.constrains("item_ids")
    @api.one
    def check_unique_invoice_address_id(self):
        addresses = self.item_ids.mapped("invoice_address_id")
        if len(addresses) > 1:
            raise UserError("The invoice address must be the "
                            "same for all the lines")
        return True


class RmaRefundItem(models.TransientModel):
    _name = "rma.refund.item"
    _description = "RMA Lines to refund"

    wiz_id = fields.Many2one(
        comodel_name="rma.refund",
        string="Wizard",
        required=True,
    )
    line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA order Line",
        required=True,
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
    name = fields.Char(
        string="Description",
        required=True,
    )
    product_qty = fields.Float(
        string="Quantity Ordered",
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
    )
    invoice_address_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice Address",
    )
    qty_to_refund = fields.Float(
        string="Quantity To Refund",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    uom_id = fields.Many2one(
        comodel_name="product.uom",
        string="Unit of Measure",
        readonly=True,
    )
    refund_policy = fields.Selection(
        selection=[
            ("no", "Not required"),
            ("ordered", "Based on Ordered Quantities"),
            ("received", "Based on Received Quantities"),
        ],
        string="Refund Policy",
    )

    @api.multi
    def _get_account(self):
        self.ensure_one()
        line = self.line_id
        product = self.product_id
        categ = product.categ_id
        if line.type == "customer":
            if product.property_account_income:
                return product.property_account_income
            if categ.property_account_income_categ:
                return categ.property_account_income_categ
        else:
            if product.property_account_expense:
                return product.property_account_expense
            if categ.property_account_income_categ:
                return categ.property_account_expense_categ
        str_warning = _("No account defined for %s") % (product.name)
        raise UserError(str_warning)

    @api.multi
    def _prepare_refund_line(self):
        self.ensure_one()
        account = self._get_account()
        values = {
            "name": self.rma_id.name,
            "origin": self.rma_id.name,
            "account_id": account.id,
            "price_unit": self.line_id.price_unit,
            "uos_id": self.line_id.uom_id.id,
            "product_id": self.product_id.id,
            "rma_line_id": self.line_id.id,
            "quantity": self.qty_to_refund,
        }
        return values
