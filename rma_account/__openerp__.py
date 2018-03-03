# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'RMA Account',
    'version': '8.0.2.0.1',
    'license': 'AGPL-3',
    'category': 'RMA',
    'summary': 'Integrates RMA with Invoice Processing',
    'author': "Akretion, Camptocamp, Eezee-it, MONK Software, Vauxoo, Eficent,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.github.com/OCA/rma',
    'depends': ['account', 'rma'],
    'demo': ['demo/rma_operation.xml'],
    'data': [
        'data/rma_policy_field_data.xml',
        'data/rma_policy_data.xml',
        'views/rma_policy_views.xml',
        'views/rma_order_view.xml',
        'views/rma_operation_view.xml',
        'views/rma_order_line_view.xml',
        'views/invoice_view.xml',
        'wizards/rma_add_invoice.xml',
        'wizards/rma_refund.xml',
    ],
    'installable': True,
    'auto_install': True,
}
