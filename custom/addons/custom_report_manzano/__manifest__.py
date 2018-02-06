{
    'name': 'Custom Report Manzanodecora',
    'description': 'Módulo Personalización Informes Manzanodecora',
    'version': '1.0',
    'author': 'David Souto & Alexandre Díaz & Darío Lodeiros (Solucións Aloxa S.L.) & Amaro Pesquero',
    'application': True,
    'data': [
        'views/ins_external_layout_footer.xml',
        'views/ins_external_layout_header.xml',
        'views/ins_external_layout.xml',
        'views/ins_report_invoice_document.xml',
        'views/ins_report_invoice.xml',
        'views/ins_report_saleorder_document.xml',
        'views/ins_report_saleorder.xml',
        'data/paper_formats.xml', ],
    'depends': ['account', 'sale', 'payment_signal', 'custom_partner_manzano', ],
    'application': True,
}
