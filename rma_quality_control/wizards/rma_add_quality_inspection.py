# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class RmaAddQualityInspection(models.TransientModel):
    _name = "rma.add_quality_inspection"
    _description = "Wizard to Quality Inspection"

    @api.model
    def default_get(self, fields):
        res = super(RmaAddQualityInspection, self).default_get(fields)
        rma_obj = self.env["rma.order"]
        rma_id = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_id:
            return res
        assert active_model == "rma.order", "Bad context propagation"

        rma = rma_obj.browse(rma_id)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
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
    operation_id = fields.Many2one(
        string="RMA Operation",
        comodel_name="rma.operation",
        domain=[("type", "=", "supplier")],
    )
    quality_inspection_ids = fields.Many2many(
        comodel_name="qc.inspection",
        relation="rma_add_quality_inspection_line_rel",
        column1="wizard_id",
        column2="quality_inspection_id",
        readonly=False,
        string="Quality Inspection",
    )

    @api.model
    def _get_rma_data(self):
        data = {
            "date_rma": fields.Datetime.now(),
            "delivery_address_id": self.rma_id.partner_id.id,
            "invoice_address_id": self.rma_id.partner_id.id
        }
        return data

    @api.multi
    def add_lines(self):
        self.ensure_one()
        rma = self.rma_id
        for line in self.quality_inspection_ids:
            line._create_rma_line_from_inspection(rma, self.operation_id)
        data_rma = self._get_rma_data()
        rma.write(data_rma)
        return {"type": "ir.actions.act_window_close"}
