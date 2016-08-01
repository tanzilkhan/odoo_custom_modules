from openerp.osv import osv, fields, orm
from openerp import api, tools, SUPERUSER_ID
from num2words import num2words

class terms_conditions(osv.Model):
    _name = 'terms.conditions'
    _description = ''
    _columns = {
        'name': fields.char('Terms & Condition', size=30),
        'is_on': fields.boolean('Active'),
        'tc_description': fields.text('Description'),
    }

class retailer_desc(osv.Model):
    _name = 'retailer.desc'
    _description = ''
    _columns = {
        'name': fields.char('Retailer Name'),
        'retailer_code': fields.char('Retailer Code'),
        'is_size': fields.boolean('Has Size'),
        'size_details': fields.one2many('account.invoice.line','name','Size Details')
    }

class size_details_line(osv.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _description = ''

    # def default_get(self, cr, uid, ids, context):
        # res = {}
        # if context:
        #     context_keys = context.keys()
        #     next_sequence = 1
        #     if 'invoice_line' in context_keys:
        #         if len(context.get('invoice_line')) > 0:
        #             next_sequence = len(context.get('invoice_line')) + 1
        # res.update({'sequence_no': next_sequence})
        # return res


    _columns = {
        # 'sequence_no':fields.integer('Sequence',default='1'),
        'euro_size': fields.many2one('retailer.euro.size','Euro Size', size=30),
        'uk_size': fields.many2one('retailer.uk.size','UK Size', size=30),
        'cn_size': fields.many2one('retailer.cn.size','CN Size', size=30),
        'size':fields.many2one('retailer.size','Size', size=30),
        'color_pan': fields.many2one('retailer.color.pan','Color/Pantone', size=30),
        'retailer_size': fields.boolean('Size Check'),
    }


class retailer_euro_size(osv.Model):
    _name = 'retailer.euro.size'
    _columns = {
        'name': fields.text('Euro Size', size=30),
    }

class retailer_uk_size(osv.Model):
    _name = 'retailer.uk.size'
    _columns = {
        'name': fields.text('UK Size', size=30),
    }

class retailer_cn_size(osv.Model):
    _name = 'retailer.cn.size'
    _columns = {
        'name': fields.text('CN Size', size=30),
    }


class retailer_size(osv.Model):
    _name = 'retailer.size'
    _columns = {
        'name': fields.text('Size', size=30),
    }

class retailer_color_pan(osv.Model):
    _name = 'retailer.color.pan'
    _columns = {
        'name': fields.text('Color/Pantone', size=30),
    }

class customer_addition(osv.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'
    _columns = {
        'shipping_name': fields.char('Name'),
        'shipping_address': fields.char('Address'),
        'shipping_mobile': fields.integer('Mobile'),
    }

class retailer_info_invoice(osv.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('other_cost.cost_amount', 'invoice_line.price_subtotal')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.total_other_cost = sum(line.cost_amount for line in self.other_cost)
        self.amount_total = self.amount_untaxed + self.total_other_cost

    # @api.one
    # @api.depends('amount_total', 'total_other_cost')
    # def _total_to_words(self):
    #     total = self.amount_total
    #     total_word = num2words(total)
    #     self.amount_total_words = total_word.upper()


    _columns = {
        'retailer_name': fields.many2one('retailer.desc', 'Retailer'),
        'style_no': fields.char('Style No.'),
        'ebiz_no': fields.char('eBiz So No.'),
        'po_no': fields.char('Po No.'),
        'goodsr_date': fields.date('Goods Ready Date'),
        'hs_code': fields.many2one('hs.code.list', 'HS Code'),
        'terms_conditions': fields.many2one('terms.conditions', 'T&C to Apply'),
        'termscond_description': fields.text('TERMS & CONDITION'),
        'amount_total_words': fields.char('Amount In Words (USD)', compute='_total_to_words', store=True, readonly='True'),
        'has_size': fields.boolean('Size Check'),
        'pi_no':fields.char('PI No'),
        'other_cost':fields.one2many('other.cost.line', 'name', 'Other Cost'),
        'total_other_cost': fields.float('Other Cost Total', store=True, compute='_compute_amount',),
    }

    _sql_constraints = [
        ('pi_no_uniq', 'UNIQUE(pi_no)', 'The PI number must be unique!'),
    ]

    @api.one
    @api.onchange('terms_conditions')
    def onchange_terms_conditions(self):
        new_var=self.terms_conditions.id
        self.termscond_description = self.env['terms.conditions'].browse(new_var).tc_description


    @api.one
    @api.depends('amount_total', 'total_other_cost')
    def _total_to_words(self):
        total = self.amount_total
        total_word = num2words(total)
        total_word_upper = total_word.upper()
        total_only_word = total_word_upper.replace("-"," ").replace(",","")
        self.amount_total_words = total_only_word + " ONLY"

    @api.onchange('retailer_name')
    def retailer_change(self):
        retailer = self.retailer_name.id
        pi_no=self.env['retailer.desc'].browse(retailer).retailer_code
        size_check = self.env['retailer.desc'].browse(retailer).is_size
        if size_check == True:
            self.has_size = True
        else:
            self.has_size = False
        self.pi_no = pi_no

    # @api.onchange('other_cost')
    # def other_cost_change(self):
    #     cost = self.other_cost
    #     self.amount_total = self.amount_total+cost

    # @api.one
    # @api.depends('other_cost.cost_amount')
    # def _compute_amount(self):
    #     self.total_other_cost = sum(line.cost_amount for line in self.other_cost)


class other_cost_line(osv.Model):
    _name = 'other.cost.line'
    _columns = {
        'name': fields.many2one('account.invoice', 'Name'),
        'other_costs': fields.many2one('other.costs.list', 'Other Costs'),
        'cost_amount': fields.float('Amount'),
    }

class other_cost_list(osv.Model):
    _name = 'other.costs.list'
    _columns = {
        'name': fields.char('Other Cost Name'),
    }

class hs_code_list(osv.Model):
    _name = 'hs.code.list'
    _columns = {
        'name': fields.char('HS CODE')
    }

    #SALE ORDER INTEGRATION WITH PI STARTS HERE
class sale_order_with_pi(osv.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('other_cost.cost_amount', 'order_line.price_subtotal')
    def _compute_amount(self):
        # self.amount_untaxed = sum(line.price_subtotal for line in self.order_line)
        self.total_other_cost = sum(line.cost_amount for line in self.other_cost)
        # self.amount_total = self.amount_untaxed + self.total_other_cost

    # @api.one
    # @api.depends('amount_total', 'total_other_cost')
    # def _total_to_words(self):
    #     total = self.amount_total
    #     total_word = num2words(total)
    #     total_word_upper = total_word.upper()
    #     total_only_word = total_word_upper.replace("-"," ").replace(",","")
    #     self.amount_total_words = total_only_word + "ONLY"

    _columns = {
        'retailer_name': fields.many2one('retailer.desc', 'Retailer'),
        'style_no': fields.char('Style No.'),
        'ebiz_no': fields.char('eBiz So No.'),
        'po_no': fields.char('Po No.'),
        'goodsr_date': fields.date('Goods Ready Date'),
        'hs_code': fields.many2one('hs.code.list', 'HS Code'),
        'terms_conditions': fields.many2one('terms.conditions', 'T&C to Apply'),
        'termscond_description': fields.text('TERMS & CONDITION'),
        'amount_total_words': fields.char('Amount In Words (USD)', compute='_total_to_words', store=True, readonly='True'),
        'has_size': fields.boolean('Size Check'),
        'pi_no':fields.char('PI No'),
        'other_cost':fields.one2many('other.cost.line', 'name', 'Other Cost'),
        'total_other_cost': fields.float('Other Cost Total', store=True, compute='_compute_amount',),
    }

    _sql_constraints = [
        ('pi_no_uniq', 'UNIQUE(pi_no)', 'The PI number must be unique!'),
    ]

    @api.one
    @api.onchange('terms_conditions')
    def onchange_terms_conditions(self):
        new_var=self.terms_conditions.id
        self.termscond_description = self.env['terms.conditions'].browse(new_var).tc_description

    @api.one
    @api.depends('amount_total', 'total_other_cost')
    def _total_to_words(self):
        total = self.amount_total
        total_word = num2words(total)
        total_word_upper = total_word.upper()
        total_only_word = total_word_upper.replace("-"," ").replace(",","")
        self.amount_total_words = total_only_word + " ONLY"

    @api.onchange('retailer_name')
    def retailer_change(self):
        retailer = self.retailer_name.id
        pi_no=self.env['retailer.desc'].browse(retailer).retailer_code
        size_check = self.env['retailer.desc'].browse(retailer).is_size
        if size_check == True:
            self.has_size = True
        else:
            self.has_size = False
        self.pi_no = pi_no

class sale_order_line_with_pi(osv.Model):
    _inherit = 'sale.order.line'

    _columns = {
        # 'sequence_no':fields.integer('Sequence',default='1'),
        'euro_size': fields.many2one('retailer.euro.size','Euro Size', size=30),
        'uk_size': fields.many2one('retailer.uk.size','UK Size', size=30),
        'cn_size': fields.many2one('retailer.cn.size','CN Size', size=30),
        'size':fields.many2one('retailer.size','Size', size=30),
        'color_pan': fields.many2one('retailer.color.pan','Color/Pantone', size=30),
        'retailer_size': fields.boolean('Size Check'),
        'delivery_from_sale_line': fields.boolean('Delivery from Sale line'),
    }

    _defaults = {
        'delivery_from_sale_line': True,
    }

#This class is made to pass values from sale_order to stock_picking (Tanzil)
class stock_move_inherit_for_passing_value(osv.Model):
    _inherit = 'stock.move'

    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):

        # Call super function
        res = super(stock_move_inherit_for_passing_value, self)._picking_assign(cr, uid, move_ids, procurement_group, location_from, location_to, context=context)

        # Get move id
        move = self.browse(cr, uid, move_ids, context=context)[0]

        # Get the values from the move
        order_obj = self.pool.get("sale.order")
        order_id = order_obj.search(cr, uid, [('name','=', move.origin)], context=context)
        vals = order_obj.read(cr, uid, order_id, ['id', 'pi_no'])

        # Get Value reference from move values
        for value in vals:
            if value.has_key('id'):
                order_ref = value['id']
            if value.has_key('pi_no'):
                pi_ref = value['pi_no']
        # If exists client reference update stock picking client_order_ref field
        if order_ref:
            stock_pick_obj = self.pool.get("stock.picking")
            stock_pick_id = stock_pick_obj.search(cr, uid, [('origin', '=', move.origin)], context=context)

            #Passing values from sale.order to stock.picking
            stock_pick_obj.write(cr, uid, stock_pick_id, {'so_number': order_ref, 'pi_number': pi_ref}, context=context)

        return