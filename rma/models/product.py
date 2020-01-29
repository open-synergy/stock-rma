# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rma_customer_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Customer RMA Operation",
    )
    rma_supplier_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Supplier RMA Operation",
    )
    rma_approval_policy = fields.Selection(
        related="categ_id.rma_approval_policy",
        readonly=True,
    )

    @api.multi
    def _get_rma_operation(self, rma_type="customer"):
        self.ensure_one()
        operation = self.categ_id._get_rma_operation(rma_type)
        if operation:
            return operation
        if rma_type == "customer":
            operation = self.rma_customer_operation_id
        else:
            operation = self.rma_supplier_operation_id
        return operation
