# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rma_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Customer RMA Operation",
    )
    supplier_rma_operation_id = fields.Many2one(
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
            operation = self.rma_operation_id
        else:
            operation = self.supplier_rma_operation_id
        return operation
