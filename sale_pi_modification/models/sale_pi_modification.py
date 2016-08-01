from openerp.osv import osv, fields
from num2words import num2words
from openerp import api, _
from decimal import Decimal


class invoice_product_variant_add(osv.Model):
    _inherit = 'account.invoice.line'
    _columns = {
        'width_size': fields.float(string='Width'),
        'gusset_size': fields.float(string='Gusset'),
        'length_size': fields.float(string='Length'),
        'flap_size': fields.float(string='Flap'),
        'dh_po': fields.char('DH PO'),
        'product_category': fields.many2one('product.category', 'Product Category'),
        'expected_date': fields.date('Estimated Production Completion'),
        'hs_code': fields.char('HS Code'),
        'order_ref': fields.char('Customer Order Ref.'),
    }



class terms_conditions(osv.Model):
    _name = 'terms.conditions'
    _description = ''
    _columns = {
        'name': fields.char('Terms & Condition', size=30),
        'is_on': fields.boolean('Active'),
        'tc_description': fields.text('Description'),
    }

class advising_bank(osv.Model):
    _name = 'advising.bank'
    _description = ''
    _columns = {
        'name': fields.char('Advising Bank', size=30),
        'is_on': fields.boolean('Active'),
        'ab_description': fields.text('Description'),
    }


class shipment_term(osv.Model):
    _name = 'shipment.term'
    # __rec_name = 'name'
    _columns = {
        'name': fields.char('Shipment Term')
    }


class shipment_mode(osv.Model):
    _name = 'shipment.mode'
    _columns = {
        'name': fields.char('Shipment Mode')
    }


class term_payment(osv.Model):
    _name = 'term.payment'
    _columns = {
        'name': fields.char('Payment Term'),
    }


class other_info_invoice(osv.Model):
    _inherit = 'account.invoice'

    _columns = {
        'terms_conditions': fields.many2one('terms.conditions', 'T&C to Apply'),
        'termscond_description': fields.text('TERMS & CONDITION'),
        'amount_total_words': fields.char('In Words',store=True, compute='_compute_total_quantity_word'),
        'other_cost': fields.float('Other Cost'),
        'total_quantity': fields.integer('TOTAL QTY(IN PCS)', store=True, readonly=True, compute='_compute_total_quantity'),
        'customer_order_no': fields.char('Customer Order NO'),
        'retailer_store': fields.many2one('retailer', 'Retailer Store'),
        'shipment_term': fields.many2one('shipment.term', 'Shipment Term'),
        'shipment_mode': fields.many2one('shipment.mode', 'Shipment Mode'),
        'customer_style_no': fields.char('Customer Style No.'),
        'retailer_mod': fields.many2one('retailer', 'Retailer'),
        'term_payment': fields.many2one('term.payment', 'Payment Term'),
        'advising_bank': fields.many2one('advising.bank', 'Advising Bank Name'),
        'ab_description': fields.text('Advising Bank'),
    }

    @api.one
    @api.onchange('terms_conditions')
    def onchange_terms_conditions(self):
        new_var = self.terms_conditions.id
        self.termscond_description = self.env['terms.conditions'].browse(new_var).tc_description

    @api.one
    @api.onchange('advising_bank')
    def onchange_terms_conditions(self):
        new_var = self.advising_bank.id
        self.ab_description = self.env['advising.bank'].browse(new_var).ab_description

    @api.onchange('amount_total', 'amount_tax')
    def total_to_words(self):
        total = self.amount_total
        total_word = num2words(Decimal(str(total)))
        self.amount_total_words = total_word.upper()

    @api.onchange('retailer_mod')
    def onchange_retailer_mod(self):
        retailer_n = self.retailer_mod.id
        self.retailer_store = retailer_n

    @api.one
    @api.depends('invoice_line.quantity')
    def _compute_total_quantity(self):
        product_obj = self.env['product.product']
        total_qty = 0
        service_qty = 0
        for line in self.invoice_line:
            for items in line:
                product_ids = items.product_id.id
                product_obj_search = product_obj.search([['id', '=', product_ids]])
                #If the Product Type is "SERVICE" it will not be counted in Total Quantity
                product_type = product_obj_search.type
                if product_type == 'service':
                    service_qty += line.quantity
                else:
                    total_qty += line.quantity

        self.total_quantity = total_qty

        # self.total_quantity = sum(line.quantity for line in self.invoice_line)

    @api.one
    @api.depends('amount_total')
    def _compute_total_quantity_word(self):
        total = self.amount_total
        total_word = num2words(Decimal(str(total)))
        self.amount_total_words = total_word.upper()


class so_product_variant_add(osv.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'width_size': fields.float(string='Width'),
        'gusset_size': fields.float(string='Gusset'),
        'length_size': fields.float(string='Length'),
        'flap_size': fields.float(string='Flap'),
        'dh_po': fields.char('DH PO'),
        'product_category': fields.many2one('product.category', 'Product Category'),
        'expected_date': fields.date('Estimated Production Completion'),
        'hs_code': fields.char('HS Code', compute='_onchange_product_hs_code_change', store=True, readonly=True,),
        'order_ref': fields.char('Customer Order Ref.'),
    }

    @api.one
    @api.depends('product_id')
    def _onchange_product_hs_code_change(self):
        new_var = self.product_id.id
        self.hs_code = self.env['product.product'].browse(new_var).hs_code


class other_info_sales_order(osv.Model):
    _inherit = 'sale.order'

    _columns = {
        'terms_conditions': fields.many2one('terms.conditions', 'T&C to Apply'),
        'termscond_description': fields.text('TERMS & CONDITION'),
        'amount_total_words': fields.char('In Words',store=True, readonly=True, compute='_compute_total_quantity_word'),
        'other_cost': fields.float('Other Cost'),
        'total_quantity': fields.integer('TOTAL QTY(IN PCS)', store=True, readonly=True, compute='_compute_total_quantity'),
        'customer_order_no': fields.char('Customer Order NO'),
        'retailer_store': fields.many2one('retailer', 'Retailer Store'),
        'shipment_term': fields.many2one('shipment.term', 'Shipment Term'),
        'shipment_mode': fields.many2one('shipment.mode', 'Shipment Mode'),
        'customer_style_no': fields.char('Customer Style No.'),
        'term_payment': fields.many2one('term.payment', 'Payment Term'),
        'advising_bank': fields.many2one('advising.bank', 'Advising Bank Name'),
        'ab_description': fields.text('Advising Bank'),
        'total_uos_quantity': fields.float('TOTAL QTY(IN PCS)', store=True, readonly=True, compute='_compute_total_uos_quantity'),
    }

    @api.one
    @api.onchange('terms_conditions')
    def onchange_terms_conditions_so(self):
        new_var = self.terms_conditions.id
        self.termscond_description = self.env['terms.conditions'].browse(new_var).tc_description

    @api.one
    @api.onchange('advising_bank')
    def onchange_terms_conditions(self):
        new_var = self.advising_bank.id
        self.ab_description = self.env['advising.bank'].browse(new_var).ab_description

    @api.onchange('retailer_mod')
    def onchange_retailer_mod_so(self):
        retailer_n = self.retailer_mod.id
        self.retailer_store = retailer_n

    @api.one
    @api.depends('order_line.product_uom_qty')
    def _compute_total_quantity(self):
        product_obj = self.env['product.product']
        total_qty = 0
        service_qty = 0
        for line in self.order_line:
            for items in line:
                product_ids = items.product_id.id
                product_obj_search = product_obj.search([['id', '=', product_ids]])
                #If the Product Type is "SERVICE" it will not be counted in Total Quantity
                product_type = product_obj_search.type
                if product_type == 'service':
                    service_qty += line.product_uom_qty
                else:
                    total_qty += line.product_uom_qty

        self.total_quantity = total_qty

        # self.total_quantity = sum(line.product_uom_qty for line in self.order_line)

    @api.one
    @api.depends('order_line.product_uos_qty')
    def _compute_total_uos_quantity(self):
        product_obj = self.env['product.product']
        total_qty = 0
        service_qty = 0
        for line in self.order_line:
            for items in line:
                product_ids = items.product_id.id
                product_obj_search = product_obj.search([['id', '=', product_ids]])
                #If the Product Type is "SERVICE" it will not be counted in Total Quantity
                product_type = product_obj_search.type
                if product_type == 'service':
                    service_qty += line.product_uos_qty
                else:
                    total_qty += line.product_uos_qty
        self.total_uos_quantity = total_qty
        # self.total_uos_quantity = sum(line.product_uos_qty for line in self.order_line)

    @api.one
    @api.depends('amount_total')
    def _compute_total_quantity_word(self):
        total = self.amount_total
        total_word = num2words(Decimal(str(total)))
        self.amount_total_words = total_word.upper()
