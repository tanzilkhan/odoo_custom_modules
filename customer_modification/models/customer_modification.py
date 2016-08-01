from openerp.osv import osv, fields

class company_type(osv.Model):
	_name = 'company.n.type'
	_columns = {
		'name': fields.char('Company Type'),
	}

class department_name(osv.Model):
	_name = 'department.name'
	_columns = {
		'name': fields.char('Department Name')
	}

class customer_modification(osv.Model):
	_inherit = 'res.partner'
	_columns = {
		'vat_no': fields.char('Vat No.'),
		# 'company_type': fields.many2one('company.n.type', 'Company Type'),
		# 'invoice_address': fields.many2one('res.partner', 'Invoice Address', help="Invoice address for current sales order.")
		'superv_name': fields.char('Supervisor Name'),
		'department_name': fields.many2one('department.name', 'Department Name'),
	}

