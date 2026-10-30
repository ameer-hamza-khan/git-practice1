from odoo import api, fields, models


class SalesBatchReportWizard(models.TransientModel):
    _name = 'sales.batch.report.wizard'
    _description = 'Sales Batch Report Wizard'

    product_id = fields.Many2one(
        'product.template',
        string='Product',
    )

    variant_ids = fields.Many2many(
        'product.product',
        string='Product Variants',
    )

    date_from = fields.Date(
        string='From Date',
    )

    date_to = fields.Date(
        string='To Date',
    )

    preview_line_ids = fields.One2many(
        'sales.batch.report.preview.line',
        'wizard_id',
        string='HAMMAD REPORT',
    )

    @api.onchange('product_id', 'variant_ids', 'date_from', 'date_to')
    def _onchange_preview_lines(self):
        for wizard in self:

            # Purana preview data clear
            wizard.preview_line_ids = [(5, 0, 0)]

            # Product select nahi kiya
            if not wizard.product_id:
                continue

            SaleLine = self.env['sale.order.line']

            domain = [
                ('order_id.state', 'in', ['sale', 'done']),
                ('product_id', '!=', False),
                (
                    'product_id.product_tmpl_id',
                    '=',
                    wizard.product_id.id
                ),
            ]

            # Variant filter
            if wizard.variant_ids:
                domain.append(
                    ('product_id', 'in', wizard.variant_ids.ids)
                )

            # From Date
            if wizard.date_from:
                domain.append(
                    (
                        'order_id.date_order',
                        '>=',
                        fields.Datetime.to_datetime(
                            wizard.date_from
                        )
                    )
                )

            # To Date
            if wizard.date_to:
                date_to_end = fields.Datetime.to_datetime(
                    wizard.date_to
                )

                date_to_end = date_to_end.replace(
                    hour=23,
                    minute=59,
                    second=59
                )

                domain.append(
                    (
                        'order_id.date_order',
                        '<=',
                        date_to_end
                    )
                )

            sale_lines = SaleLine.search(domain)

            # Same sorting as report
            sale_lines = sale_lines.sorted(
                key=lambda line:
                line.order_id.date_order
                or fields.Datetime.now()
            )

            preview_lines = []

            for sale_line in sale_lines:

                move_lines = sale_line.move_ids.mapped(
                    'move_line_ids'
                )

                # Only delivered records
                move_lines = move_lines.filtered(
                    lambda ml: ml.picking_id.state == 'done'
                )

                if move_lines:

                    for move_line in move_lines:

                        preview_lines.append(
                            (0, 0, {
                                'product': sale_line.product_id
                                .product_tmpl_id.display_name,

                                'variant': sale_line.product_id
                                .display_name,

                                'customer': sale_line.order_id
                                .partner_id.display_name,

                                'order_date': sale_line.order_id
                                .date_order,

                                'qty': move_line.quantity,

                                'sale_rate': sale_line.price_unit,

                                'lot': move_line.lot_id.name or '',
                            })
                        )

                else:

                    preview_lines.append(
                        (0, 0, {
                            'product': sale_line.product_id
                            .product_tmpl_id.display_name,

                            'variant': sale_line.product_id
                            .display_name,

                            'customer': sale_line.order_id
                            .partner_id.display_name,

                            'order_date': sale_line.order_id
                            .date_order,

                            'qty': sale_line.qty_delivered,

                            'sale_rate': sale_line.price_unit,

                            'lot': '',
                        })
                    )

            wizard.preview_line_ids = preview_lines

    def action_print_report(self):
        return self.env.ref(
            'sales_batch_report.action_sales_batch_report'
        ).report_action(self)


class SalesBatchReportPreviewLine(models.TransientModel):
    _name = 'sales.batch.report.preview.line'
    _description = 'Sales Batch Report Preview Line'

    wizard_id = fields.Many2one(
        'sales.batch.report.wizard',
        string='Wizard',
        ondelete='cascade',
    )

    product = fields.Char(
        string='Product',
        readonly=True,
    )

    variant = fields.Char(
        string='Product Variant',
        readonly=True,
    )

    customer = fields.Char(
        string='Customer',
        readonly=True,
    )

    order_date = fields.Datetime(
        string='Order Date',
        readonly=True,
    )

    qty = fields.Float(
        string='Qty',
        readonly=True,
    )

    sale_rate = fields.Float(
        string='Sale Rate',
        readonly=True,
    )

    lot = fields.Char(
        string='Lot / Serial Number',
        readonly=True,
    )