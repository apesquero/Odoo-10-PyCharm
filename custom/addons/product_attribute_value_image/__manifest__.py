# -*- encoding: utf-8 -*-
{
    'name': 'Product Attribute Value Image',
    'version': "10.0.1.0",
    'author': 'Amaro Pesquero Rodríguez',
    'category': 'Sales Management',
    'depends': ['product',
                'web_tree_image',
                'product_variant_configurator',
                'sale_variant_configurator',
                ],
    'data': ['views/product_attribute_value_view.xml',
             'views/product_configurator_attribute.xml',
             ],
    'installable': True,
}
