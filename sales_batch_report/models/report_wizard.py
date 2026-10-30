from odoo import api, fields, models


class SalesBatchReport(models.AbstractModel):
    _name = 'report.sales_batch_report.sales_batch_report_template'
    _description = 'Sales Batch Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['sales.batch.report.wizard'].browse(docids)
        lines = []

        SaleLine = self.env['sale.order.line']

        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
            ('product_id', '!=', False),
        ]

        # Product filter
        if wizard.product_id:
            domain.append(
                ('product_id.product_tmpl_id', '=', wizard.product_id.id)
            )

        # Variant filter
        if wizard.variant_ids:
            domain.append(
                ('product_id', 'in', wizard.variant_ids.ids)
            )

        # From Date filter
        if wizard.date_from:
            domain.append(
                ('order_id.date_order', '>=', fields.Datetime.to_datetime(wizard.date_from))
            )

        # To Date filter - include the complete day
        if wizard.date_to:
            date_to_end = fields.Datetime.to_datetime(wizard.date_to)
            date_to_end = date_to_end.replace(
                hour=23,
                minute=59,
                second=59
            )

            domain.append(
                ('order_id.date_order', '<=', date_to_end)
            )

        sale_lines = SaleLine.search(domain)

        # Sort by order date
        sale_lines = sale_lines.sorted(
            key=lambda line: line.order_id.date_order or fields.Datetime.now()
        )

        for sale_line in sale_lines:

            move_lines = sale_line.move_ids.mapped('move_line_ids')

            # Only delivered records
            move_lines = move_lines.filtered(
                lambda ml: ml.picking_id.state == 'done'
            )

            if move_lines:

                for move_line in move_lines:

                    lines.append({
                        'product': sale_line.product_id.product_tmpl_id.display_name,
                        'variant': sale_line.product_id.display_name,
                        'customer': sale_line.order_id.partner_id.display_name,
                        'order_date': sale_line.order_id.date_order,
                        'qty': move_line.quantity,
                        'sale_rate': sale_line.price_unit,
                        'lot': move_line.lot_id.name or '',
                    })

            else:

                lines.append({
                    'product': sale_line.product_id.product_tmpl_id.display_name,
                    'variant': sale_line.product_id.display_name,
                    'customer': sale_line.order_id.partner_id.display_name,
                    'order_date': sale_line.order_id.date_order,
                    'qty': sale_line.qty_delivered,
                    'sale_rate': sale_line.price_unit,
                    'lot': '',
                })

        return {
            'doc_ids': docids,
            'doc_model': 'sales.batch.report.wizard',
            'docs': wizard,
            'lines': lines,
        }