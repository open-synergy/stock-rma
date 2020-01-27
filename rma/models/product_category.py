# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = "product.category"

    rma_customer_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Customer RMA Operation",
    )
    rma_supplier_operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Supplier RMA Operation",
    )

    @api.multi
    def _get_rma_operation(self, rma_type="customer"):
        self.ensure_one()
        operation = False
        if rma_type == "customer":
            operation = self.rma_customer_operation_id
        else:
            operation = self.rma_supplier_operation_id
        if not operation:
            operation = self.env["rma.operation"].search(
                [("type", "=", rma_type)], limit=1)
            if len(operation) == 0:
                operation = False
        return operation
