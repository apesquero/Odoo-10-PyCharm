# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

class TestWizard(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestWizard, self).setUp(*args, **kwargs)
        # Add test setup code here...

    def test_populate_tasks(self):
        "Populate tasks buttons should add two tasks"
        # Add test code...
