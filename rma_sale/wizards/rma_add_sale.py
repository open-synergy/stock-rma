# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class RmaAddSale(models.TransientModel):
    _name = "rma_add_sale"
    _description = "Wizard to add rma lines"

    @api.model
    def default_get(self, fields):
        res = super(RmaAddSale, self).default_get(fields)
        rma_obj = self.env["rma.order"]
        rma_id = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_id:
            return res
        assert active_model == "rma.order", "Bad context propagation"

        rma = rma_obj.browse(rma_id)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
        res["sale_id"] = False
        res["sale_line_ids"] = False
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
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Order",
    )
    sale_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        relation="rma_add_sale_add_line_rel",
        column1="sale_line_id",
        column2="rma_add_sale_id",
        readonly=False,
        string="Sale Lines",
    )

    @api.model
    def _get_rma_data(self):
        data = {
            "date_rma": fields.Datetime.now(),
            "delivery_address_id": self.sale_id.partner_id.id,
            "invoice_address_id": self.sale_id.partner_id.id
        }
        return data

    @api.model
    def _get_existing_sale_lines(self):
        existing_sale_lines = []
        for rma_line in self.rma_id.rma_line_ids:
            existing_sale_lines.append(rma_line.sale_line_id)
        return existing_sale_lines

    @api.multi
    def add_lines(self):
        existing_sale_lines = self._get_existing_sale_lines()
        rma = self.rma_id
        for line in self.sale_line_ids:
            # Load a PO line only once
            if line not in existing_sale_lines:
                line._create_rma_line_from_so_line(rma)
        data_rma = self._get_rma_data()
        rma.write(data_rma)
        return {"type": "ir.actions.act_window_close"}
