from openerp.osv import osv, fields


class net_price_add(osv.Model):
	_inherit = 'product.template'
	_columns = {
		'net_price': fields.float('Net Price', size=120),
		'product_width': fields.float('Width', size=16),
		'product_gusset': fields.float('Gusset', size=16),
		'product_length': fields.float('Length', size=16),
		'product_flap': fields.float('Flap', size=16),
	}

