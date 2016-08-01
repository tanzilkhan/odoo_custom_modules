from openerp.osv import osv, fields


class other_attr(osv.Model):
    _name = 'other.attr'
    _columns = {
        'name': fields.char('Other Attribute')
    }


class net_price_add(osv.Model):
    _inherit = 'product.template'
    _columns = {
        'net_price': fields.float('Net Price', size=120),
        'hs_code': fields.char('HS Code', size=120),
        'product_width': fields.float('Width', size=16),
        'w_uos_id': fields.many2one('product.uom', string='Width UOM', ondelete='set null', index=True),
        'product_gusset': fields.float('Gusset', size=16),
        'g_uos_id': fields.many2one('product.uom', string='Gusset UOM', ondelete='set null', index=True),
        'product_length': fields.float('Length', size=16),
        'l_uos_id': fields.many2one('product.uom', string='Length UOM', ondelete='set null', index=True),
        'product_flap': fields.float('Flap', size=16),
        'f_uos_id': fields.many2one('product.uom', string='Flap UOM', ondelete='set null', index=True),
        'other_attrs': fields.many2one('other.attr', 'Other Attribute', size=32),
    }
