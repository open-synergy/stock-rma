# Copyright 2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class RmaRouteTemplate(models.Model):
    _name = "rma.route_template"
    _description = "RMA Route Template"

    name = fields.Char(
        string="RMA Route Template",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        required=True,
        default=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    note = fields.Text(
        string="Note",
    )
    in_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Inbound Route",
        domain=[
            ("rma_selectable", "=", True),
        ],
    )
    out_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Outbound Route",
        domain=[
            ("rma_selectable", "=", True),
        ],
    )
    customer_to_supplier = fields.Boolean(
        string="The customer will send to the supplier",
        default=False,
    )
    supplier_to_customer = fields.Boolean(
        string="The supplier will send to the customer",
        default=False,
    )
    in_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Inbound Warehouse",
    )
    out_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Outbound Warehouse",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Send To This Company Location",
    )

    @api.multi
    def _get_route_template_policy(self):
        self.ensure_one()
        return {
            "in_route_id": self.in_route_id.id,
            "out_route_id": self.out_route_id.id,
            "in_warehouse_id": self.in_warehouse_id.id,
            "out_warehouse_id": self.out_warehouse_id.id,
            "location_id": self.location_id.id,
        }
