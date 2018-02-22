{
    'name': 'Custom Sale Order',
    'description': 'Módulo que modifica el aspecto de la vista sale order',
    'version': '10.1.1',
    'author': 'Amaro Pesquero',
    'application': True,
    'data': [
             'views/inherit_sale_order.xml', ],
    'category': 'Sales',
    'depends': ['sale',
                'sale_variant_configurator',
                'product_attribute_value_image'],
    'application': True,
}
