# Copyright 2020 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Eezee-It, MONK Software, Vauxoo
# Copyright 2013 Camptocamp
# Copyright 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "RMA Account",
    "version": "11.0.1.2.1",
    "license": "AGPL-3",
    "category": "RMA",
    "author": "Akretion, Camptocamp, Eezee-it, MONK Software, Vauxoo, Eficent,"
              "Odoo Community Association (OCA)",
    "website": "http://www.github.com/OCA/rma",
    "depends": [
        "account",
        "rma"
    ],
    "data": [
        "data/rma_policy_field_data.xml",
        "data/rma_policy_data.xml",
        "views/rma_policy_views.xml",
        "views/rma_order_view.xml",
        "views/rma_operation_view.xml",
        "views/rma_order_line_view.xml",
        "views/invoice_view.xml",
        "wizards/rma_add_invoice.xml",
        "wizards/rma_refund.xml",
    ],
    "installable": True,
    "auto_install": True,
}
