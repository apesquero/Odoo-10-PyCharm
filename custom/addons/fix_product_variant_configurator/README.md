# Fixed product variants

## product_product.py
We need this hack to trigger the compute function, otherwise attr_line.price_extra always returns 0.0 here (possible Odoo bug, it seems Odoo does not behave well with a computed variable on NewID 'child' of another NewID)