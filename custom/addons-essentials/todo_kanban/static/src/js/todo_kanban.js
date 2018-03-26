/**
 * Created by apesq on 24/03/2018.
 */

odoo.define('todo.kanban', function(require) { // define here
    'use strict';

    var Widget = require('web.Widget');

    var Component = Widget.extend({
        template: 'demo.template',
        events: {},
        init: function () {
            this._super.apply(this, arguments);
        },
        willStart: function () {
            return this._super.apply(this, arguments).then(function () {
            })
        },
        start: function () {}
    });
});

