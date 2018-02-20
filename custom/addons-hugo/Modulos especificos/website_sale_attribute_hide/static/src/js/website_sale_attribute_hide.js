odoo.define('website_sale_attribute_hide.website_sale', function (require) {
"use strict";

var hook = require('website_sale_hook.website_sale');

function attribute_node_change ($attr_li) {
    if ($attr_li.find('.wsa_hide').length > 0) {
        var enableds = $attr_li.find("input.js_variant_change:radio:enabled, option:enabled");
        
        if (enableds.length <= 1) {
            $attr_li.css('display', 'none');
        }
        else {
            $attr_li.removeAttr('style');
        }
    }
};

var original_attribute_node_change = hook.attribute_node_change;

hook.attribute_node_change = function($attr_li) {
    attribute_node_change ($attr_li);
    original_attribute_node_change($attr_li); //super
};

//initialization
$('.oe_website_sale').each(function () {
    var $parent = $('div.js_product', $(this));
    
    $parent.find('li.wsa_hide_parent').each(function() { attribute_node_change($(this)); });
});

});

