# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odooodoo import models, fields
from odoo import tools


class SupplierRmaAnalysis(models.Model):
    _name = "rma.supplier_rma_analysis"
    _description = "Supplier RMA Analysis Analysis"
    _auto = False

    rma_id = fields.Many2one(
        string="# RMA",
        comodel_name="rma.order",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("done", "Done"),
        ],
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    date_rma = fields.Datetime(
        string="Order Date",
    )
    date_deadline = fields.Datetime(
        string="Deadline",
    )
    operation_id = fields.Many2one(
        string="RMA Operation",
        comodel_name="rma.operation",
    )
    assigned_to_id = fields.Many2one(
        string="Assigned To",
        comodel_name="res.users",
    )
    requested_by_id = fields.Many2one(
        string="Requested By",
        comodel_name="res.users",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
    )
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
    )
    lot_id = fields.Many2one(
        string="Lot/Serial Number",
        comodel_name="stock.production.lot",
    )
    product_qty = fields.Float(
        string="Ordered Qty",
    )
    price_unit = fields.Float(
        string="Price Unit",
    )
    in_warehouse_id = fields.Many2one(
        string="Inbound Warehouse",
        comodel_name="stock.warehouse",
    )
    out_warehouse_id = fields.Many2one(
        string="Outbound Warehouse",
        comodel_name="stock.warehouse",
    )
    qty_to_receive = fields.Float(
        string="Qty To Receive",
    )
    qty_incoming = fields.Float(
        string="Incoming Qty",
    )
    qty_received = fields.Float(
        string="Qty Received",
    )
    qty_to_deliver = fields.Float(
        string="Qty To Deliver", copy=False,
    )
    qty_outgoing = fields.Float(
        string="Outgoing Qty",
    )
    qty_delivered = fields.Float(
        string="Qty Delivered",
    )

    def _select(self):
        select_str = """
        SELECT
            a.id AS id,
            a.rma_id AS rma_id,
            b.state AS state,
            a.date_rma AS date_rma,
            a.date_deadline AS date_deadline,
            a.operation_id AS operation_id,
            a.assigned_to AS assigned_to_id,
            a.requested_by AS requested_by_id,
            c.commercial_partner_id AS partner_id,
            a.product_id AS product_id,
            a.lot_id AS lot_id,
            a.company_id AS company_id,
            a.in_warehouse_id AS in_warehouse_id,
            a.out_warehouse_id AS out_warehouse_id,
            SUM(a.product_qty) AS product_qty,
            SUM(a.price_unit) AS price_unit,
            SUM(a.qty_to_receive) AS qty_to_receive,
            SUM(a.qty_incoming) AS qty_incoming,
            SUM(a.qty_received) AS qty_received,
            SUM(a.qty_to_deliver) AS qty_to_deliver,
            SUM(a.qty_outgoing) AS qty_outgoing,
            SUM(a.qty_delivered) AS qty_delivered
        """
        return select_str

    def _from(self):
        from_str = """
        rma_order_line AS a
        """
        return from_str

    def _where(self):
        where_str = """
        WHERE 1 = 1 AND
        b.type = 'supplier'
        """
        return where_str

    def _join(self):
        join_str = """
        JOIN rma_order AS b ON a.rma_id = b.id
        JOIN res_partner AS c ON a.partner_id = c.id
        """
        return join_str

    def _group_by(self):
        group_str = """
        GROUP BY
            a.id,
            a.rma_id,
            b.state,
            a.date_rma,
            a.date_deadline,
            a.operation_id,
            a.assigned_to,
            a.requested_by,
            c.commercial_partner_id,
            a.product_id,
            a.lot_id,
            a.company_id,
            a.in_warehouse_id,
            a.out_warehouse_id
        """
        return group_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        # pylint: disable=locally-disabled, sql-injection
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            %s
            %s
            %s
        )""" % (
            self._table,
            self._select(),
            self._from(),
            self._join(),
            self._where(),
            self._group_by()
        ))
