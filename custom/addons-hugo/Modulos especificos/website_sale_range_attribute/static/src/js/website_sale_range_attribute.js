odoo.define('website_sale_range_attribute.website_sale', function (require) {
"use strict";

var hook = require('website_sale_hook.website_sale');


var timer_id = null;

window.addEventListener('unload', function(event) { //TODO check if this is needed
    if (timer_id != null) {
        clearTimeout(timer_id);
    }
    timer_id = null;
});

function timer_func($range_input) {
    timer_id = null;
    
    var new_value = +$range_input.val();
    var value_nodes = $range_input.parent().parent().find('input.js_variant_change');
    for (var i = 0; i < value_nodes.length; i++) {
        var $input_node = $(value_nodes[i]);
        
        var max_range = +$input_node.data('max-range');
        var min_range = +$input_node.data('min-range');
        if ((new_value >= min_range) && (new_value <= max_range)) { //max-min range exact frontier value done by order
            $input_node.prop('checked', true);
            $input_node.change();
            break;
        }
    }
}

function update_out_range_message($input, update_price) {
    var $out_range_message = $("span.out-range-message", $input.parent().parent());
    
    var new_value = +$input.val();
    var max_range = +$input.data('range-max');
    var min_range = +$input.data('range-min');
    
    if ((new_value >= min_range) && (new_value <= max_range)) {
        $out_range_message.hide();
        if (update_price) {
            if (timer_id != null) {
                clearTimeout(timer_id);
            }
            timer_id = setTimeout(timer_func, 800, $input);
        }
    }
    else {
        $out_range_message.show();
    }
}

function attribute_node_change($li) {
    var $input = $('input.range-attribute', $li);
    if ($input.length <= 0){
        return;
    }
    
    var max_value = null;
    var min_value = null;
    $li.find('input.radio-range:not([disabled])').each(function () {
        var temp_min = +$(this).data('min-range');
        var temp_max = +$(this).data('max-range');
        
        if ((min_value == null) || (min_value>temp_min)) {
            min_value = temp_min;
        }
        if ((max_value == null) || (max_value<temp_max)) {
            max_value = temp_max;
        }
    });
    
    $input.data('range-min', min_value);
    $input.data('range-max', max_value);
    update_out_range_message($input, false);
}

var original_attribute_node_change = hook.attribute_node_change;

hook.attribute_node_change = function($attr_li) {
    attribute_node_change ($attr_li);
    original_attribute_node_change($attr_li); //super
};

$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    
    // hack to add and rome from cart with json
    $(oe_website_sale).on('click', 'a.js_add_range_input', function (ev) {
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.parent().find("input.range-attribute");
        //var product_id = +$input.closest('*:has(input[name="product_id"])').find('input[name="product_id"]').val();
        var range_min = parseFloat($input.data("range-min") || 0);
        var range_max = parseFloat($input.data("range-max") || Infinity);
        //TODO period
        var new_quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val(),10);
        var quantity = new_quantity > range_min ? (new_quantity < range_max ? new_quantity : range_max) : range_min;
        if (quantity != $input.val()) {
            $input.val(quantity);
            $input.change();
        }
        return false;
    });
    
    $(oe_website_sale).on('keypress', 'input.range-attribute', function (ev) {
        if ((ev.keyCode == 39) || (ev.keyCode == 37)) { //left and right
            return;
        }

        var code = (ev.keyCode ? ev.keyCode : ev.which);
        if (!(
                (code >= 48 && code <= 57) //numbers
                || (code == 8) //backspace
                || (code == 44) //comma
            )
            || (code == 44 && $(this).val().indexOf(',') != -1)
        ) {
            ev.preventDefault();
        }
    });
    
    $(oe_website_sale).on('keyup', 'input.range-attribute', function (ev) {
        $(this).change();
    });
    
    $(oe_website_sale).on('change', 'input.range-attribute', function (ev) {
        var $input = $(ev.currentTarget);
        
        update_out_range_message($input, true);
    });
    
    //initialization (set up every range input to the minimum range of its checked radio input, which will be the first one)
    var inputs = $(oe_website_sale).find('input.range-attribute');
    //for (var i=0; i < inputs.length; i++) { //TODO check
    //    var $linput = $(inputs[i]);
    //    var $selected_input = $('input.js_variant_change:checked', $linput.parent().parent());
    //    var min_value = +$selected_input.data('min-range');
    //    $linput.val(min_value);
    //}
    //needed in case it is the first one
    if (inputs.length > 0) {
        var $finput = $(inputs[0]);
        attribute_node_change($finput.parent().parent().parent());
    }
        
});

});

