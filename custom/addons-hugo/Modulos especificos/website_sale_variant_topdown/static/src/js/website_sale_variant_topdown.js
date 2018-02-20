odoo.define('website_sale_variants_topdown.website_sale', function (require) {
"use strict";

var hook = require('website_sale_hook.website_sale');
var variants_change_input = hook.variants_change_input;
var original_variants_change_input = variants_change_input; //TODO

variants_change_input = function (ev) {
    var $ul = $(ev.target).closest('.js_add_cart_variants');
    var $parent = $ul.closest('.js_product');
    var website_sale_variant_type = $parent.attr('website_sale_variant_type');
    
    if (website_sale_variant_type == 'topdown') {
        var $product_id = $parent.find('input.product_id').first();
        var $price = $parent.find(".oe_price:first .oe_currency_value");
        var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
        var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
        var variant_ids = $ul.data("attribute_value_ids");
        var $attr_name = $(ev.target).closest('strong.js_attribute_name');
        var index = parseInt($attr_name.attr('attr_index'), 10);
        var total_indexes = $ul.find('input.js_attr_total_indexes').first().val(); //TODO check this
        var values = [];
        $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
            values.push(+$(this).val());
        });
        //$parent.find("label").removeClass("text-muted css_not_available");
        
        //TODO the whole algo expect the value array to be ordered. Check that the modification of get_attribute_value_ids python func works.
        //TODO prices?
        var relevant_values = values.slice(0, index+1)
        //var next_valids = []
        //for (var k in variants_ids) {
        //    if (_isEmpty(_.difference(variant_ids[k][1].slice(0, index+1), relevant_values))) {
        //        next_valids.push(variants_ids[k]);
        //    }
        //}
        next_valids = _.filter(variants_ids, function(k) { _isEmpty(_.difference(k[1].slice(0, index+1), relevant_values)) });
        
        for (var i=index+1; i<total_indexes; i++) {
            var valids = []
            for (var k in next_valids) {
                valids.push(next_valids[k][1][i]);
            }
            var $attr_ul = $ul.find("strong[attr_index='" + i + "']:first").next('ul.list-unstyled'); //TODO first
            $attr_ul.find('label.control-label').each(function () {
                if ($(this).find('input.js_variant_change').val() in valids) { //TODO this and the rest of the code only works on input not selects
                    $(this).removeClass("text-muted css_not_available");
                }
                else {
                    $(this).addClass("css_not_available");
                }
            });
            var value_selected = 0;
            if (values[i] in valids) {
                value_selected = values[i];
            }
            else {
                //select the first valid one
                value_selected = valids[0];
                $attr_ul.find("input.js_variant_change[value='" + value_selected + "']:first").attr('checked',true); //does not trigger change event
            }
            //modify next_valids with the current selection
            next_valids = _.filter(next_valids, function(vl) { vl[1][i] == value_selected });
        }
        
        //select product_id
        var product_id = _.find(next_valids, function(vl) { _isEmpty(_.difference(vl[1],values)) })[0];
    }
    else {
        original_variants_change_input(ev); //super
    }
};

});

