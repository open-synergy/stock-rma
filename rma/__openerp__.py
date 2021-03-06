# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'RMA (Return Merchandise Authorization)',
    'version': '8.0.3.0.0',
    'license': 'AGPL-3',
    'category': 'RMA',
    'summary': 'Introduces the return merchandise authorization (RMA) process '
               'in Odoo',
    'author': "Akretion, Camptocamp, Eezee-it, MONK Software, Vauxoo, Eficent,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.github.com/OCA/rma',
    'depends': ['stock', 'mail', 'procurement'],
    'demo': ['demo/stock_demo.xml',
             ],
    'data': ['security/rma.xml',
             'security/ir.model.access.csv',
             'data/rma_sequence.xml',
             'data/rma_policy_field_data.xml',
             'data/rma_policy_data.xml',
             'data/stock_data.xml',
             'data/rma_operation.xml',
             'menu.xml',
             'views/rma_policy_field_views.xml',
             'views/rma_policy_views.xml',
             'views/rma_route_template_views.xml',
             'views/rma_order_view.xml',
             'views/rma_operation_view.xml',
             'views/rma_order_line_view.xml',
             'views/stock_view.xml',
             'views/stock_warehouse.xml',
             'views/product_view.xml',
             'views/procurement_view.xml',
             'wizards/rma_make_picking_view.xml',
             'wizards/rma_add_stock_move_view.xml',
             'wizards/stock_config_settings.xml',
             'wizards/rma_order_line_make_supplier_rma_view.xml',
             'reports/customer_rma_analysis.xml',
             'reports/supplier_rma_analysis.xml',
             ],
    'installable': True,
    'auto_install': False,
}
