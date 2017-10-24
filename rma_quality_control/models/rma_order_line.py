# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class RmaOrderLine(models.Model):
    _inherit = "rma.order.line"

    quality_inspection_id = fields.Many2one(
        comodel_name="qc.inspection",
        string="Quality Inspection",
        ondelete="restrict",
    )
