odoo.define('product_price_type.MultiDimensionTableField', function (require) {
"use strict";

var core = require('web.core');
var Model = require('web.Model');
var form_common = require('web.form_common');
var data = require('web.data');

var MultiDimensionTable = form_common.AbstractField.extend({
	/** GLOBAR VARS **/
	_MODE : { TABLE_1D:'table_1d', TABLE_2D:'table_2d' },

	/** WIDGET PARAMS **/
    template: 'product_price_type.MultiDimensionTableView',

    /** INITIALIZE FUNCTIONS **/
    init: function () {
        this._super.apply(this, arguments);

        this.tableType_field = this.node.attrs.mode || false;
        this.tableType = this._MODE.TABLE_1D;

        this.ds_model = new data.DataSetSearch(this, this.view.model);
        this.model_product_prices_table = new Model("product.prices_table");

        this.isInvisible = true;
        this.inEditMode = false;
        this.values = [];
    },

    start: function () {
        this.view.on("change:actual_mode", this, this._on_check_visibility_mode);
        this._on_check_visibility_mode();
        return this._super();
    },

	// TODO: ELIMINADO POR EFICIENCIA, CUANDO SEPA MÁS DE JS, LO ARREGLO
    /** FIELD VALUE MANAGEMENT **/
    // commit_value: function () {
    // 	var self = this;
    // 	this.$el.find('.o_mdtable_item').each(function(){
    // 		var $this = $(this);
    // 		var _id = $this.data('id');
    // 		var _x = $this.data('x');
    // 		var _y = $this.data('y') || false;
    // 		var _v = $this.find('input').val();
	//
    // 		if (self._get_item(_x, _y).value != _v) {
    // 			self.model_product_prices_table.call('write', [[_id], {'value': _v}]);
    // 			self._set_item(_x, _y, _v);
    // 		}
	// 	});
    //
    //  return this._super();
    // },
    
    read_value: function () {
        var self = this;
        
        this.model_product_prices_table.call('search_read', [[['id', 'in', this.get_value()]]])
        	.then(function(results){
        		self.values = results;
        		self.render_value();
        	});
    },
    
    set_value: function(value_) {
    	var _super = this._super(value_);
    	this.read_value();
    	return _super;
    },
    
    /** RENDER WIDGET **/
    render_value: function () {
    	if (!this.isInvisible && Number.isInteger(this.view.datarecord.id)) {
	    	var self = this;
	    	this.ds_model.read_ids([this.view.datarecord.id], [this.tableType_field])
	        .then(function (results) {
	            self.tableType = results[0][self.tableType_field];
	            self._render_widget();
	        });
    	}
    },
    
    _render_widget: function () {    	
    	if (typeof this.values === 'undefined')
    		return;
    	
    	var self = this;
    	var table = $('<table>');
    	table.addClass('col-md-12');
    	
    	// Get Headers
		var hx = [],
			hy = [];
		this.values.forEach(function(item, index) {
			hx.push(item.pos_x);
			hy.push(item.pos_y);
		});
		hx = [...new Set(hx)];
		hy = [...new Set(hy)];
		///
		
		// Table HTML
    	if (this.tableType == this._MODE.TABLE_2D) {
    		var thead_src = '<th>&nbsp;</th>';
    		for (var i in hx) { thead_src += `<th>${hx[i]}</th>`; }
    		table.append(`<thead><tr>${thead_src}</tr></thead>`);
    		
    		var tbody_src = '';
    		for (var y in hy) {
    			tbody_src += `<tr><th>${hy[y]}</th>`;
    			for (var x in hx) {
    				var item = this._get_item(hx[x], hy[y]);
    				var value = parseFloat(item.value).toFixed(2) || '0.00';
    				tbody_src += `<td class='o_mdtable_item ${!item.value && 'o_mdtable_item_empty'}' data-id='${item.id}' data-x='${item.pos_x}' data-y='${item.pos_y}'>${value}</td>`;
    			}
    			tbody_src += '</tr>';
    		}
	    	table.append(`<tbody>${tbody_src}</tbody>`);
    	} else {
    		var thead_src = '';
    		for (var i in hx) { thead_src += `<th>${hx[i]}</th>`; }
    		table.append(`<thead><tr>${thead_src}</tr></thead>`);
    		
			var tbody_src = '';
			for (var x in hx) {
				var item = this._get_item(hx[x], false);
				var value = parseFloat(item.value).toFixed(2) || 0.00;
				tbody_src += `<td class='o_mdtable_item ${!item.value && 'o_mdtable_item_empty'}' data-id='${item.id}' data-x='${item.pos_x}' data-y='false'>${value}</td>`;
			}
		
	    	table.append(`<tbody><tr>${tbody_src}</tr></tbody>`);
    	}
    	table.appendTo(this.$el.empty());
    	
    	// Events
    	this.$el.find('.o_mdtable_item').on('click', function(ev){
    		var $this = $(this);
    		var inEditMode = self.view.get("actual_mode") === 'edit';
    		if (!inEditMode) {
    			var $button = $(document).find(".oe_form_button_edit");
                $button.openerpBounce();
                ev.stopPropagation();
                core.bus.trigger('click', ev);
    		}
    	});
    	
    	this._redraw_table_items();
    },
    
    /** EVENT LISTENERS **/
    _on_check_visibility_mode: function () {
    	this.isInvisible = this.view.get("actual_mode") === 'create';
    	this.inEditMode = this.view.get("actual_mode") === 'edit';
    	this._redraw_table_items();
    },
    
    /** HELPER FUNCTIONS **/
    _redraw_table_items: function() {
    	var self = this;
		this.$el.find('.o_mdtable_item').each(function(){
			var $this = $(this);
			if (self.inEditMode) {
				var bckgColor = ($this.hasClass('o_mdtable_item_empty'))?'#deb390':'initial';
				$this.html(`<input type='text' value='${$this.text()}' style='background-color:${bckgColor}'/>`);
			} else {
				$this.text($this.find('input').val());
			}
		});
		
		if (self.inEditMode) {
	    	this.$el.find('.o_mdtable_item input').on('change', function(ev){
	    		var $this = $(this);
	    		var _x = $this.parent().data('x');
	    		var _y = $this.parent().data('y') || false;
	    		var _v = $this.val();
	    		var _cv = self._get_item(_x, _y).value;
	    		
	    		if (_cv != _v) {
	    			if (!_v || _v == 0) {
	    				$this.animate({'background-color': '#deb390'});
	    			} else {
	    				$this.animate({'background-color': '#eae9e9'});
	    			}
	    		} else {
	    			if ($this.parent().hasClass('o_mdtable_item_empty')) {
	    				$this.animate({'background-color': '#deb390'});
	    			} else {
	    				$this.animate({'background-color': 'initial'});
	    			}
	    		}
	    	});
		}
    },
    
    _get_item(x, y) {
    	var value = false;
    	this.values.forEach(function(item, index) {
    		if ((!y && item.pos_x == x) || (item.pos_x == x && item.pos_y == y)) {
    			value = item;
    			return;
    		}
    	});
    	
    	return value;
    },
    
    _set_item(x, y, value) {
    	var self = this;
    	this.values.forEach(function(item, index) {
    		if ((!item.pos_y && item.pos_x == x) || (item.pos_x == x && item.pos_y == y)) {
    			item.value = value;
    			self.values[index] = item;
    			return;
    		}
    	});
    },
});

core.form_widget_registry.add('mdtable', MultiDimensionTable);

return MultiDimensionTable;
});