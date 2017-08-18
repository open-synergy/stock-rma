# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


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
