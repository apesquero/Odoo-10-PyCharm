# -*- coding: utf-8 -*-
import models


def init_assign_qty(cr, registry):
    """
    This post-init-hook will update all existing mrp.bom.line
    """
    cr.execute('UPDATE mrp_bom_line'
               '   SET qty_eval = CAST(product_qty as VARCHAR)')
