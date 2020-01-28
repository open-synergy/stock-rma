# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_rma_delivery_address = fields.Selection(
        selection=[
            (0, "Invoicing and shipping addresses are always the same "
                "(Example: services companies)"),
            (1, "Display 3 fields on rma: partner, invoice address, delivery "
                "address"),
        ],
        string="Addresses",
        implied_group="rma.group_rma_delivery_invoice_address",
    )
