# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "RMA Purchase",
    "version": "8.0.2.0.0",
    "category": "RMA",
    "summary": "RMA from PO",
    "license": "AGPL-3",
    "author": "Eficent",
    "website": "http://www.github.com/eficent/stock-rma",
    "depends": [
        "rma_account",
        "purchase",
    ],
    "data": [
        "views/rma_order_view.xml",
        "views/rma_order_line_view.xml",
        "wizards/rma_add_purchase.xml",
    ],
    "installable": True,
    "auto_install": False,
}
