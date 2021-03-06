# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class RmaLineMakeSupplierRma(models.TransientModel):
    _inherit = "rma.order.line.make.supplier.rma"

    @api.model
    def _prepare_supplier_rma_line(self, rma, item):
        res = super(RmaLineMakeSupplierRma, self)._prepare_supplier_rma_line(
            rma, item)
        if res['operation_id']:
            operation = self.env['rma.operation'].browse(res['operation_id'])
            res['refund_policy_id'] = operation.refund_policy_id.id
        return res
