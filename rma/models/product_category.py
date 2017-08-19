# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class ProductCategory(models.Model):
    _inherit = "product.category"

    rma_approval_policy = fields.Selection(
        selection=[
            ('one_step', 'One step'),
            ('two_step', 'Two steps'),
        ],
        string="RMA Approval Policy",
        required=True,
        default='one_step',
        help="Options: \n "
             "* One step: Always auto-approve RMAs that only contain "
             "products within categories with this policy.\n"
             "* Two steps: A RMA containing a product within a category with "
             "this policy will request the RMA manager approval.",
    )
    rma_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Customer RMA Operation",
    )
    supplier_rma_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Supplier RMA Operation",
    )

    @api.multi
    def _get_rma_operation(self, rma_type="customer"):
        self.ensure_one()
        operation = False
        if rma_type == "customer":
            operation = self.rma_operation_id
        else:
            operation = self.supplier_rma_operation_id
        if not operation:
            operation = self.env["rma.operation"].search(
                [("type", "=", rma_type)], limit=1)
            if len(operation) == 0:
                operation = False
        return operation
