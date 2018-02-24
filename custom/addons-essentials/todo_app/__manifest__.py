# -*- coding: utf-8 -*-

{
    'name': 'To-Do Application',
    'description': 'Manage your personal To-Do task.',
    'author': 'Daniel Reis',
    'depends': ['base'],
    'data': ['security/ir.model.access.csv',
             'security/todo_access_rules.xml',
             'views/todo_menu.xml',
             'views/todo_view.xml'],
    'application': True,
}