# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "RMA Repair",
    "version": "8.0.1.1.0",
    "license": "AGPL-3",
    "category": "RMA",
    "summary": "Links RMA with Repairs.",
    "author": "Eficent",
    "website": "http://www.github.com/OCA/rma",
    "depends": ["rma_account", "mrp_repair"],
    "data": [
        "data/mrp_repair_sequence.xml",
        "data/rma_policy_field_data.xml",
        "data/rma_policy_data.xml",
        "views/rma_policy_views.xml",
        "views/rma_order_view.xml",
        "views/rma_operation_view.xml",
        "views/mrp_repair_view.xml",
        "wizards/rma_order_line_make_repair_view.xml",
        "views/rma_order_line_view.xml",
        ],
    "installable": True,
    "auto_install": True,
}
