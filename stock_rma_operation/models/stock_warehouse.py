# -*- coding: utf-8 -*-
# Copyright 2017 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rma_cust_route_id = fields.Many2one(
        string="RMA Customer Route",
        comodel_name="stock.location.route",
    )
    rma_sup_route_id = fields.Many2one(
        string="RMA Supplier Route",
        comodel_name="stock.location.route",
    )

    @api.multi
    def _prepare_rma_location(self):
        self.ensure_one()
        parent_location = self.lot_stock_id
        data = {
            "name": _("RMA"),
            "location_id": parent_location.id,
            "usage": "internal",
            "active": True

        }
        return data

    @api.multi
    def _create_rma_loc(self):
        self.ensure_one()
        obj_loc = self.env["stock.location"]
        rma_loc = obj_loc.create(
            self._prepare_rma_location())
        return rma_loc

    @api.multi
    def _prepare_rma_cust_in_sequence(self):
        self.ensure_one()
        data = {
            "name": self.code + " - RMA Customer In",
            "prefix": self.code + "/RCI/",
            "padding": 6
        }
        return data

    @api.multi
    def _prepare_rma_cust_out_sequence(self):
        self.ensure_one()
        data = {
            "name": self.code + " - RMA Customer Out",
            "prefix": self.code + "/RCO/",
            "padding": 6
        }
        return data

    @api.multi
    def _prepare_rma_sup_in_sequence(self):
        self.ensure_one()
        data = {
            "name": self.code + " - RMA Supplier In",
            "prefix": self.code + "/RSI/",
            "padding": 6
        }
        return data

    @api.multi
    def _prepare_rma_sup_out_sequence(self):
        self.ensure_one()
        data = {
            "name": self.code + " - RMA Supplier Out",
            "prefix": self.code + "/RSI/",
            "padding": 6
        }
        return data

    @api.multi
    def _prepare_rma_cust_in_type(self):
        self.ensure_one()
        obj_sequence = self.env['ir.sequence']

        sequence = obj_sequence.create(
            self._prepare_rma_cust_in_sequence())

        data = {
            "name": _("RMA Customer In"),
            "warehouse_id": self.id,
            "sequence_id": sequence.id,
            "code": "incoming",
        }
        return data

    @api.multi
    def _prepare_rma_cust_out_type(self):
        self.ensure_one()
        obj_sequence = self.env['ir.sequence']

        sequence = obj_sequence.create(
            self._prepare_rma_cust_out_sequence())

        data = {
            "name": _("RMA Customer Out"),
            "warehouse_id": self.id,
            "sequence_id": sequence.id,
            "code": "outgoing",
        }
        return data

    @api.multi
    def _prepare_rma_sup_in_type(self):
        self.ensure_one()
        obj_sequence = self.env['ir.sequence']

        sequence = obj_sequence.create(
            self._prepare_rma_sup_in_sequence())

        data = {
            "name": _("RMA Supplier In"),
            "warehouse_id": self.id,
            "sequence_id": sequence.id,
            "code": "incoming",
        }
        return data

    @api.multi
    def _prepare_rma_sup_out_type(self):
        self.ensure_one()
        obj_sequence = self.env['ir.sequence']

        sequence = obj_sequence.create(
            self._prepare_rma_sup_out_sequence())

        data = {
            "name": _("RMA Supplier Out"),
            "warehouse_id": self.id,
            "sequence_id": sequence.id,
            "code": "outgoing",
        }
        return data

    @api.multi
    def _create_rma_cust_in_type(self):
        self.ensure_one()
        obj_type = self.env["stock.picking.type"]
        pick_type = obj_type.create(
            self._prepare_rma_cust_in_type())
        return pick_type

    @api.multi
    def _create_rma_cust_out_type(self):
        self.ensure_one()
        obj_type = self.env["stock.picking.type"]
        pick_type = obj_type.create(
            self._prepare_rma_cust_out_type())
        return pick_type

    @api.multi
    def _create_rma_sup_in_type(self):
        self.ensure_one()
        obj_type = self.env["stock.picking.type"]
        pick_type = obj_type.create(
            self._prepare_rma_sup_in_type())
        return pick_type

    @api.multi
    def _create_rma_sup_out_type(self):
        self.ensure_one()
        obj_type = self.env["stock.picking.type"]
        pick_type = obj_type.create(
            self._prepare_rma_sup_out_type())
        return pick_type

    @api.multi
    def button_create_rma_cust_in_type(self):
        for wh in self:
            pick_type = wh._create_rma_cust_in_type()
            wh.rma_cust_in_type_id = pick_type.id

    @api.multi
    def button_create_rma_cust_out_type(self):
        for wh in self:
            pick_type = wh._create_rma_cust_out_type()
            wh.rma_cust_out_type_id = pick_type.id

    @api.multi
    def button_create_rma_sup_in_type(self):
        for wh in self:
            pick_type = wh._create_rma_sup_in_type()
            wh.rma_sup_in_type_id = pick_type.id

    @api.multi
    def button_create_rma_sup_out_type(self):
        for wh in self:
            pick_type = wh._create_rma_sup_out_type()
            wh.rma_sup_out_type_id = pick_type.id

    @api.model
    def create(self, values):
        new_wh = super(StockWarehouse, self).create(values)
        rma_cust_in_type = new_wh._create_rma_cust_in_type()
        rma_cust_out_type = new_wh._create_rma_cust_out_type()
        rma_sup_in_type = new_wh._create_rma_sup_in_type()
        rma_sup_out_type = new_wh._create_rma_sup_out_type()
        rma_loc = new_wh._create_rma_loc()
        new_wh.write({
            "rma_cust_in_type_id": rma_cust_in_type.id,
            "rma_cust_out_type_id": rma_cust_out_type.id,
            "rma_sup_in_type_id": rma_sup_in_type.id,
            "rma_sup_out_type_id": rma_sup_out_type.id,
            "lot_rma_id": rma_loc.id,
        })
        rma_cust_route = new_wh._create_route_rma_cust()
        rma_sup_route = new_wh._create_route_rma_sup()
        new_wh.write({
            "rma_cust_route_id": rma_cust_route.id,
            "rma_sup_route_id": rma_sup_route.id,
        })
        return new_wh

    @api.multi
    def _prepare_rma_cust_pull_rule(self, step=False):
        self.ensure_one()
        result = []
        rma_cust_in_type = self.rma_cust_in_type_id
        rma_cust_out_type = self.rma_cust_out_type_id
        cust_loc = self.env["ir.property"].get(
            "property_stock_customer",
            "res.partner")
        # RMA Cust Inbound
        result.append((0, 0, {
            "name": self.code + ": RMA Customer Inbound",
            "location_id": self.lot_rma_id.id,
            "warehouse_id": self.id,
            "action": "move",
            "location_src_id": cust_loc.id,
            "picking_type_id": rma_cust_in_type.id,
            "procure_method": "make_to_stock",
        }))
        # RMA Cust Outbound
        result.append((0, 0, {
            "name": self.code + ": RMA Customer Outbound",
            "location_src_id": self.lot_rma_id.id,
            "warehouse_id": self.id,
            "action": "move",
            "location_id": cust_loc.id,
            "picking_type_id": rma_cust_out_type.id,
            "procure_method": "make_to_stock",
        }))
        return result

    @api.multi
    def _prepare_rma_sup_pull_rule(self, step=False):
        self.ensure_one()
        result = []
        rma_supp_in_type = self.rma_sup_in_type_id
        rma_sup_out_type = self.rma_sup_out_type_id
        sup_loc = self.env["ir.property"].get(
            "property_stock_supplier",
            "res.partner")
        # RMA Supp Inbound
        result.append((0, 0, {
            "name": self.code + ": RMA Supplier Inbound",
            "location_src_id": sup_loc.id,
            "warehouse_id": self.id,
            "action": "move",
            "location_id": self.lot_rma_id.id,
            "picking_type_id": rma_supp_in_type.id,
            "procure_method": "make_to_stock",
        }))
        # RMA Supp Outbound
        result.append((0, 0, {
            "name": self.code + ": RMA Supplier Outbound",
            "location_id": sup_loc.id,
            "warehouse_id": self.id,
            "action": "move",
            "location_src_id": self.lot_rma_id.id,
            "picking_type_id": rma_sup_out_type.id,
            "procure_method": "make_to_stock",
        }))
        return result

    @api.multi
    def _prepare_route_rma_cust(self):
        self.ensure_one()
        return {
            "name": self.name + ": RMA Customer",
            "product_categ_selectable": False,
            "product_selectable": False,
            "warehouse_selectable": False,
            "sale_selectable": False,
            "rma_selectable": True,
            "pull_ids": self._prepare_rma_cust_pull_rule(),
        }

    @api.multi
    def _prepare_route_rma_sup(self):
        self.ensure_one()
        return {
            "name": self.name + ": RMA Supplier",
            "product_categ_selectable": False,
            "product_selectable": False,
            "warehouse_selectable": False,
            "sale_selectable": False,
            "rma_selectable": True,
            "pull_ids": self._prepare_rma_sup_pull_rule(),
        }

    @api.multi
    def _create_route_rma_cust(self):
        self.ensure_one()
        obj_route = self.env["stock.location.route"]
        return obj_route.create(
            self._prepare_route_rma_cust())

    @api.multi
    def _reset_route_rma_cust(self):
        self.ensure_one()
        route = self.rma_cust_route_id
        criteria = [
            ("route_id", "=", route.id),
        ]
        self.env["procurement.rule"].search(
            criteria).unlink()
        route.write({
            "pull_ids": self._prepare_rma_cust_pull_rule(),
        })

    @api.multi
    def _reset_route_rma_sup(self):
        self.ensure_one()
        route = self.rma_sup_route_id
        criteria = [
            ("route_id", "=", route.id),
        ]
        self.env["procurement.rule"].search(
            criteria).unlink()
        route.write({
            "pull_ids": self._prepare_rma_sup_pull_rule(),
        })

    @api.multi
    def _create_route_rma_sup(self):
        self.ensure_one()
        obj_route = self.env["stock.location.route"]
        return obj_route.create(
            self._prepare_route_rma_sup())

    @api.multi
    def button_create_route_rma_cust(self):
        for wh in self:
            route = self._create_route_rma_cust()
            wh.write({
                "rma_cust_route_id": route.id,
            })

    @api.multi
    def button_create_route_rma_sup(self):
        for wh in self:
            route = self._create_route_rma_sup()
            wh.write({
                "rma_sup_route_id": route.id,
            })

    @api.multi
    def button_create_rma_loc(self):
        for wh in self:
            rma_loc = wh._create_rma_loc()
            self.lot_rma_id = rma_loc.id

    @api.multi
    def button_reset_route_rma_sup(self):
        for wh in self:
            self._reset_route_rma_sup()

    @api.multi
    def button_reset_route_rma_cust(self):
        for wh in self:
            self._reset_route_rma_cust()
