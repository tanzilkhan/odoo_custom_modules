from openerp.osv import osv, fields

class customer_modification(osv.Model):
	_inherit = 'res.partner'
	_columns = {
		'vat_no': fields.char('Vat No.'),
	}