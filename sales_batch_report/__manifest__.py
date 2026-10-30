{
    'name': 'Sales Batch Report',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Product Variant Sales Batch PDF Report',
    'description': """
        Sales Batch Report
        ==================
        This module provides a wizard to generate a PDF report
        showing product, variants, customers, order date, quantity,
        sale rate, and lot/serial numbers.
    """,
    'author': 'Custom',
    'depends': [
        'sale',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_report_wizard_views.xml',
        'reports/sales_report_template.xml',
        'reports/sales_report_action.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}