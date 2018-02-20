odoo.define('website_sale_attribute_hierarchy.website_sale', function (require) {
"use strict";

var ajax = require('web.ajax');
var hook = require('website_sale_hook.website_sale');
require('website_sale_range_attribute.website_sale');


function processValueRules(hierarchy, parent_value_id, rules) {
    var parent_value_rules = hierarchy[parent_value_id];
    for (var child_attr_id in parent_value_rules) {
        if (_.isUndefined(rules[child_attr_id])) {
            rules[child_attr_id] = parent_value_rules[child_attr_id];
        }
        else {
            rules[child_attr_id] = _.intersection(rules[child_attr_id], parent_value_rules[child_attr_id]);
        }
    }
}

function get_range_value($value_node) {
    var $range_input = $('input.range-attribute', $value_node.parent().parent().parent().parent());
    return +$range_input.val();
}

var loading_timer_id = null;
var ajax_result = null;

window.addEventListener('unload', function(event) { //TODO check if this is needed
    if (loading_timer_id != null) {
        clearTimeout(loading_timer_id);
    }
    loading_timer_id = null;
});

function loading_timer_func($loading_error) {
    loading_timer_id = null;
    
    $loading_error.show();
}

function actualize_price (product_id, value_list, $parent) {
    var qty = $parent.find('input[name="add_qty"]').val();
    if (ajax_result != null) {
        //ajax_result.abort(); //FIXME!!
    }
    //TODO get the identifier of the last ajax call and ignore the previous ones
    ajax_result = ajax.jsonRpc("/shop/get_unit_price", 'call', {'product_ids': false,
                                                                'add_qty': parseInt(qty),
                                                                'product_template_id': product_id,
                                                                'data_from_template': value_list, })
    .then(function (data) {
        ajax_result = null;
        if (loading_timer_id != null) {
            clearTimeout(loading_timer_id);
            loading_timer_id = null;
        }
        //getting the qty to multiply
        //var qty = +$("input[name='add_qty']", $parent).val();
        //var total = qty * (+data);
        $('span.oe_currency_value', $parent).html(data);
        
        $('span.oe_price_loading', $parent).hide();
        $('b.oe_price', $parent).show();
    });
    
    $('b.oe_price', $parent).hide();
    $('span.oe_price_loading', $parent).show();
    $('span.oe_price_loading_error', $parent).hide();
    
    if (loading_timer_id != null) {
        clearTimeout(loading_timer_id);
    }
    loading_timer_id = setTimeout(loading_timer_func, 10000, $('span.oe_price_loading_error', $parent));
}

function variants_change_input(ev) {
        var $ul = $(ev.target).closest('ul.js_add_cart_variants');
        var $parent = $ul.closest('div.js_product');
        var hierarchy = $ul.data("attribute-extra");
        
        var selected_value_id = +$(ev.target).val();
        var selected_rules = {};
        var unprocessed_rule_index = 0;
        var selected_value_nodes = $parent.find('input.js_variant_change:checked, select.js_variant_change');
        var value_list = [];
        
        for (var i = 0; i < selected_value_nodes.length; i++) {
            var $value_node = $(selected_value_nodes[i]);
            var value_id = +$value_node.val();
            var attr_id = +$value_node.data('attribute');
            var value_dict = { 'value': value_id, 'attribute': attr_id };
            if ($value_node.hasClass('radio-range')) {
                value_dict['r'] = get_range_value($value_node);
            }
            value_list.push(value_dict);
            processValueRules(hierarchy, value_id, selected_rules);
            
            if (value_id == selected_value_id) {
                unprocessed_rule_index = i + 1;
                break;
            }
        }
        
        for (var i=unprocessed_rule_index; i < selected_value_nodes.length; i++) {
            var $value_node = $(selected_value_nodes[i]);
            var $values_ul = $value_node.closest('ul, select.js_variant_change');
            var attr_id = +$value_node.data('attribute');
            
            var valid_values = selected_rules[attr_id];
            var reselect = false;
            if ((!_.isUndefined(valid_values)) && (valid_values.length > 0)) { //if empty means all valid
                $values_ul.find("input.js_variant_change:radio, option").each(function () {
                    var self = this;
                    if (_.contains(valid_values, +$(self).val())) {
                        $(self).prop('disabled', false);
                        $(self).parent('label').removeClass('css_not_available'); //this could be removed but just to follow how Odoo is doing it
                    }
                    else {
                        //we are going to disable the selected value, reselect a new one
                        if (($(self).prop('checked')) || ($(self).prop('selected'))) {
                            reselect = true;
                            var $label_color = $(self).parent('label.css_attribute_color');
                            
                            if ($label_color.length) {
                                $label_color.removeClass('active');
                            }
                        }
                        
                        $(self).prop('disabled', true);
                        $(self).parent('label').addClass('css_not_available');
                    }
                });
            }
            else {
                $values_ul.find("input.js_variant_change:radio, option").each(function () {
                    var self = this;
                    $(self).prop('disabled', false);
                    $(self).parent('label').removeClass('css_not_available');
                });
            }
            
            if (reselect == true) {
                var $first_active = $values_ul.find("input.js_variant_change:radio:not([disabled])").first();
                if ($first_active.length) {
                    $first_active.prop('checked', true);
                    var $label_color = $first_active.parent('label.css_attribute_color');
                    if ($label_color.length) {
                        $label_color.addClass('active');
                    }
                }
                else {
                    $first_active = $values_ul.find("option:not([disabled])").first();
                    $first_active.prop('selected', true);
                }
                
                $value_node = $first_active; //this is necessary for the price and processing of the rules that comes next
            }
            
            var $attr_li = $values_ul.closest('li');
            hook.attribute_node_change($attr_li);
            
            //processing the rules of this node for the next ones
            var value_id = +$value_node.val();
            var value_dict = { 'value': value_id, 'attribute': attr_id };
            if ($value_node.hasClass('radio-range')) {
                value_dict['r'] = get_range_value($value_node);
            }
            value_list.push(value_dict);
            processValueRules(hierarchy, value_id, selected_rules);
        }
        
        //adding the single value attributes (that are not rangeinput types)
        var $singles_div =$('div.single-value-attributes', $parent);
        var singles_children = $singles_div.children('span');
        for (var i = 0; i < singles_children.length; i++) {
            var single_spam = singles_children[i];
            
            var attr_id = +$(single_spam).data('attribute');
            var value_id = +$(single_spam).data('value');
            
            var value_dict = { 'value': value_id, 'attribute': attr_id };
            value_list.push(value_dict);
        }
        
        $ul.data('current-value-list', value_list);
        
        //actualize price
        var product_id = +$parent.children('input.product_template_id').val();
        actualize_price(product_id, value_list, $parent);
        
        //save the value_list jsonizied so it will be sent with the form
        $ul.children('input.current-value-list').val(JSON.stringify(value_list));
}

var qty_timer_id = null;

window.addEventListener('unload', function(event) { //TODO check if this is needed
    if (qty_timer_id != null) {
        clearTimeout(qty_timer_id);
    }
    qty_timer_id = null;
});

function change_qty_input(ev) {
    if (qty_timer_id != null) {
        clearTimeout(qty_timer_id);
    }
    qty_timer_id = setTimeout(qty_timer_func, 800, $(ev.target));
}

function qty_timer_func($target) {
    qty_timer_id = null;
    
    var $parent = $target.closest('div.js_product');
    var $ul = $parent.children('ul.js_add_cart_variants');
    var product_id = +$parent.children('input.product_template_id').val();
    var value_list = $ul.data('current-value-list');
    
    actualize_price(product_id, value_list, $parent);
}

//initialization
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    
    var $parent = $('div.js_product', $(oe_website_sale));
    var website_sale_variant_type = $parent.data('website-sale-variant-type');
    
    if (website_sale_variant_type == 'hierarchy') {
        $(oe_website_sale).on("change", "input[name='add_qty']", change_qty_input);
        
        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change', variants_change_input);
        
        $parent.removeClass('css_not_available');
        var $values_ul = $('ul.js_add_cart_variants', $parent);
        var $first_li = $('li:first', $values_ul);
        if ($first_li.length) {
            var first_li_input_list = $first_li.find("input.js_variant_change:radio");
            if (first_li_input_list.length) {
                var $checked_input = null;
                first_li_input_list.each(function () {
                    $(this).parent('label').removeClass('css_not_available');
                    if ($(this).prop('checked')) {
                        $checked_input = $(this);
                    }
                });
                $checked_input.trigger('change');
            }
            else { //it is select, not input
                var first_li_option_list = $first_li.find("select.js_variant_change option");
                first_li_option_list.each(function () {
                    $(this).removeClass('css_not_available');
                });
                $("select.js_variant_change", $first_li).trigger('change');
            }
        }
        else { //it means it is a product without attributes, just a single product
            $("input[name='add_qty']", $parent).trigger('change');
        }
    }
});

});

