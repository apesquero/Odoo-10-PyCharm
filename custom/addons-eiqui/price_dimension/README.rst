PRICE DIMENSION
=============
Compute product prices and supplier prices based on dimensions "Width" and "Height".

- Adds new fields "Width" and "Height" in sale.order_line and purchuase.order_line
- Adds new tab "Price Type" for select how compute the price in product.template, product.product and product.supplierinfo:
    + Standard: Like Odoo works
    + Table 1D: Uses the new field "width" inside order and purchase line
    + Table 2D: Uses the new field "width" and "height" inside order and purchase line
	+ Area: Multiplies the price by "width" and "height" values defined inside order/purchase line
- Adds new widget for view/edit table prices values
- Adds wizards for import .xsl/.xsls files
- Adds new field in product.attribute.value for select between:
    + Standard: Like Odoo works
    + Percentage: Compute 'extra_price' for apply percentage of the product price


Table Prices Headers are computed like ranges [MIN, MAX), last col and row don't need values:

* Example table (2D):
[       ][  100  ][  120  ][  150  ]
[  100  ][ 9.40  ][ 10.80 ][       ]
[  120  ][ 10.60 ][   0   ][       ]
[  140  ][ 12.30 ][ 15.10 ][       ]
[  180  ][ 13.60 ][ 18.60 ][       ]
[  200  ][       ][       ][       ]

Possible ranges:
  + Width: 100-120 | 120-150
  + Height: 100-120 | 120-140 | 140-180 | 180-200

Select values (108x132) = (100x120) = 10.60 
Possible max. values (149.99x199.99) = (120x180) = 18.60

Select values (120x120) = 0 = Dimensions aren't available

Credits
=======

Creator
------------

* Alexandre Díaz <alex@aloxa.eu>
