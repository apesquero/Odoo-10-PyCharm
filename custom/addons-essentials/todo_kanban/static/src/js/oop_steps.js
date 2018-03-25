/**
 * Created by apesq on 25/03/2018.
 */

odoo.define('todo.kanban', function(require) { // define here
    'use strict';

    var Class = require('web.Class'); // import here

    var Ticket = Class.extend({
        init: function (values) {
            Object.assign(this, values);
        },
    });

    var MagicTicket = Ticket.extend({
        init: function (values) {
            this._supper.apply(this, arguments);
            this.magic = this.init_magic();
        },
        init_magic: function () {
            // do stuff
        },
    });
});

