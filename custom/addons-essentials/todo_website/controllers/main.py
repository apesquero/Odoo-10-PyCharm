# -*- coding: utf-8 -*-

from odoo import http

class Todo(http.Controller):

    @http.route('/helloworld', auth='public')
    def hello_world(self):
        return '<h1>Hello World!</h1>'