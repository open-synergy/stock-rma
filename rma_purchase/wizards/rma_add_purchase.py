# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class RmaAddPurchase(models.TransientModel):
    _name = "rma_add_purchase"
    _description = "Wizard to add rma lines"

    @api.model
    def default_get(self, fields):
        res = super(RmaAddPurchase, self).default_get(fields)
        rma_obj = self.env["rma.order"]
        rma_id = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_id:
            return res
        assert active_model == "rma.order", "Bad context propagation"

        rma = rma_obj.browse(rma_id)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
        res["purchase_id"] = False
        res["purchase_line_ids"] = False
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
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Order",
    )
    operation_id = fields.Many2one(
        comodel_name="rma.operation",
        domain=[("type", "=", "supplier")],
        )
    purchase_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="rma_add_purchase_add_line_rel",
        column1="purchase_line_id",
        column2="rma_add_purchase_id",
        readonly=False,
        string="Purcahse Order Lines",
    )

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
            # Load a PO line only once
            if line not in existing_purchase_lines:
                line._create_rma_line_from_po_line(rma, self.operation_id)
        data_rma = self._get_rma_data()
        rma.write(data_rma)
        return {"type": "ir.actions.act_window_close"}
