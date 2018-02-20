odoo.define('website_sale_hook.website_sale', function (require) {
"use strict";

require('website_sale.website_sale'); //making sure this code runs after the code at website_sale.website_sale

$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    
    var $parent = $('div.js_product', $(oe_website_sale));
    var website_sale_variant_type = $parent.data('website-sale-variant-type');
    
    if ((!_.isUndefined(website_sale_variant_type)) && (website_sale_variant_type != 'standard')) {
        //the associated function runs first, correcting some thing it does
        $parent.find(".oe_default_price").hide();
        $parent.find("#add_to_cart").removeClass("disabled");
        //removing the default associated function so other modules can attach a new one ("overriding" it)
        $(oe_website_sale).off('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]');
        
        //"overriding" for prices
        $(oe_website_sale).off("change", "input[name='add_qty']");
        
        //$(oe_website_sale).off('change', 'input.js_product_change');
    }
});

return {
          attribute_node_change: function($attr_li) { return; },
       };

});

