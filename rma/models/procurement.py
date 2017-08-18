# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    rma_line_id = fields.Many2one(
        comodel_name="rma.order.line",
        string="RMA",
        ondelete="set null",
    )

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        if procurement.rma_line_id:
            line = procurement.rma_line_id
            res["rma_line_id"] = line.id
            if line.delivery_address_id:
                res["partner_id"] = line.delivery_address_id.id
            else:
                res["partner_id"] = line.rma_id.partner_id.id
        return res


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    rma_id = fields.Many2one(
        comodel_name="rma.order",
        string="RMA",
        ondelete="set null",
    )
