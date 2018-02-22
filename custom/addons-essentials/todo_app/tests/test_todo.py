# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase

class TestTodo(TransactionCase):

    def test_create(self):
        "Create a simple Todo"
        Todo = self.env['todo.task']
        task = Todo.create({'name': 'Test Task'})
        self.assertEqual(task.is_done, False)

        # Test Toggle Done
        task.do_toggle_done()
        self.assertTrue(task.is_done)

        # Test Clear Done
        Todo.do_clear_done()
        self.assertFalse(task.active)

