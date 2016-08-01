from openerp.osv import osv, fields, orm
from openerp import api, _
from openerp.report import report_sxw

import xlwt
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _

_ir_translation_name = 'daily.sale.order.xls'

class esq_export_lc_ci_report(orm.TransientModel):
    _name='esq.sale.pi.report'

    @api.one
    @api.depends('daily_order_rcv_rel.model_quantity')
    def _total_quantity_of_report(self):
        total_sub_quantity = 0.0
        for line in self.daily_order_rcv_rel:
            total_sub_quantity += line.model_quantity
        self.total_quantity = total_sub_quantity

    @api.one
    @api.depends('daily_order_rcv_rel.model_unit_price')
    def _total_unit_price_of_report(self):
        total_sub_unit_price = 0.0
        for line in self.daily_order_rcv_rel:
            total_sub_unit_price += line.model_unit_price
        self.total_amount = total_sub_unit_price


    _columns = {
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),

        #Columns for report. These will be shown in one2many
        'daily_order_rcv_rel': fields.one2many('daily.order.rcv', 'name', 'Delivery Order Receive'),
        'total_quantity': fields.float('Total Quantitty', compute='_total_quantity_of_report'),
        'total_amount': fields.float('Total Amount', compute='_total_unit_price_of_report'),
    }

    @api.one
    @api.onchange('date_from','date_to')
    def sale_order_receive_report(self):
        product_list = []

        if self.date_from != False and self.date_to != False:
            sale_order_obj = self.env['sale.order']
            sale_order_search = sale_order_obj.search([['date_order', '>=', self.date_from],['date_order','<=',self.date_to]])

            product_obj = self.env['product.product']
            product_template_obj = self.env['product.template']

            #Each sale order item loop
            for sale in sale_order_search:
                #Each order line on sale order loop
                for order in sale.order_line:
                    #orm for getting value from product template with product id
                    product_search = product_obj.search([['id','=',order.product_id.id]])
                    product_template_id = product_search.product_tmpl_id.id
                    product_template_search = product_template_obj.search([['id','=',product_template_id]])

                    product_list.append((0, 0, {
                        #Values from sale_order
                        'so_date': sale.date_order,
                        'customer':sale.partner_id.id,
                        'pi_no': sale.name,
                        'so_retailer': sale.retailer_mod.id,
                        #Values from sale_order_line
                        'model': order.product_id.id,
                        'description': order.name,
                        'model_uom': order.product_uom.id,
                        'model_quantity': order.product_uom_qty,
                        'model_unit_price': order.price_unit,
                        'so_amount': order.price_subtotal,
                        #Values from product template
                        'model_width': product_template_search.product_width,
                        'model_length': product_template_search.product_length,
                        'model_gusset': product_template_search.product_gusset,
                        'model_flap': product_template_search.product_flap,
                        }))

            self.daily_order_rcv_rel = product_list

    #Report printing button function in model
    def sale_summary_print(self, cr, uid, ids, context=None):
        return {
          'type': 'ir.actions.report.xml',
          'report_name': 'sale_pi_modification.sale_pi_report_document',
          'context': context,
        }

    # THIS FUNCTION TRIGGERS BUTTON ACTION FOR EXCEL PRINT (TANZIL)
    def xls_export(self, cr, uid, ids, context=None):
        datas = {}
        return {'type': 'ir.actions.report.xml',
                'report_name': 'sale.order.xls',
                'datas': datas}

#Table for one2many. These will be shown on wizard one2many
class daily_order_rcv(orm.TransientModel):
    _name='daily.order.rcv'

    _columns = {
        'name': fields.many2one('esq.sale.pi.report','Daily Order Receive'),
        'so_date': fields.date('Date'),
        'customer': fields.many2one('res.partner', 'Customer'),
        'model': fields.many2one('product.product','Model'),
        'description': fields.char('Description'),
        'model_width': fields.float('Width'),
        'model_length': fields.float('Length'),
        'model_gusset': fields.float('Gusset'),
        'model_flap': fields.float('Flap'),
        'model_uom': fields.many2one('product.uom', 'UOM'),
        'model_quantity': fields.float('Quantity'),
        'model_unit_price': fields.float('Unite Price'),
        'so_amount': fields.float('Amount'),
        'pi_no': fields.char('PI No.'),
        'so_retailer': fields.many2one('retailer', 'Retailer')
    }

#Report Printing Class
class sale_pi_report_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(sale_pi_report_print, self).__init__(cr, uid, name, context=context)
        self.context = context
        self.localcontext.update({
            # 'get_approval_stage': self._get_approval_stage,
        })

#Calling Report Printing Class
class esq_export_lc_report_template(osv.AbstractModel):
    _name = 'report.sale_pi_modification.sale_pi_report_document'
    _inherit = 'report.abstract_report'
    _template = 'sale_pi_modification.sale_pi_report_document'
    _wrapped_report_class = sale_pi_report_print

#####################################
##### Excel Report Print Wizard######
#####################################
class sale_order_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_order_xls_parser, self).__init__(cr, uid, name, context=context)
        purchase_obj = self.pool.get('esq.sale.pi.report')
        self.context = context
        #wanted_list = purchase_obj._report_xls_fields(cr, uid, context)
        #template_changes = purchase_obj._report_xls_template(cr, uid, context)

        self.localcontext.update({
            'datetime': datetime,
             # 'wanted_list': ['name','desc','unit','product_qty'],
            #HERE ARE THE LIST OF ALL THE COLUMNS OF ONE2MANY WHICH VALUE SHOULD BE PRINTED
             'wanted_list': ['so_date','customer','model','description', 'model_width','model_length','model_gusset', 'model_flap','model_uom','model_quantity','model_unit_price','so_amount','pi_no','so_retailer'],

            #'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src


class sale_order_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(sale_order_xls, self).__init__(  name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf( aml_cell_format + _xs['left'], num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf( aml_cell_format + _xs['right'],  num_format_str=report_xls.decimal_format)

        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf( rt_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)

        self.col_specs_template = {
            'so_date': {
                'header': [1, 12, 'text', _render("_('Sale Order Date')")],
                'lines': [1, 0, 'text', _render("line.so_date or ''")]
                },
            'customer': {
                'header': [1, 12, 'text', _render("_('Customer')")],
                'lines': [1, 0, 'text', _render("line.customer.name or ''")]
            },
            'model': {
                'header': [1, 12, 'text', _render("_('Model')")],
                'lines': [1, 0, 'text', _render("line.model.name or ''")]
            },
            'description': {
                'header': [1, 12, 'text', _render("_('Description')")],
                'lines': [1, 0, 'text', _render("line.description or ''")]
            },
            'model_width': {
                'header': [1, 12, 'text', _render("_('Width')")],
                'lines': [1, 0, 'number', _render("line.model_width or ''")]
            },
            'model_length': {
                'header': [1, 12, 'text', _render("_('Length')")],
                'lines': [1, 0, 'number', _render("line.model_length or ''")]
            },
            'model_gusset': {
                'header': [1, 12, 'text', _render("_('Gusset')")],
                'lines': [1, 0, 'number', _render("line.model_gusset or ''")]
            },
            'model_flap': {
                'header': [1, 12, 'text', _render("_('Flap')")],
                'lines': [1, 0, 'number', _render("line.model_flap or ''")]
            },
            'model_uom': {
                'header': [1, 12, 'text', _render("_('UOM')")],
                'lines': [1, 0, 'text', _render("line.model_uom.name or ''")]
            },
            'model_quantity': {
                'header': [1, 12, 'text', _render("_('Quantity')")],
                'lines': [1, 0, 'number', _render("line.model_quantity or ''")]
            },
            'model_unit_price': {
                'header': [1, 12, 'text', _render("_('Unit Price')")],
                'lines': [1, 0, 'number', _render("line.model_unit_price or ''")]
            },
            'so_amount': {
                'header': [1, 12, 'text', _render("_('Amount')")],
                'lines': [1, 0, 'number', _render("line.so_amount or ''")]
            },
            'pi_no': {
                'header': [1, 12, 'text', _render("_('PI No.')")],
                'lines': [1, 0, 'text', _render("line.pi_no or ''")]
            },
            'so_retailer': {
                'header': [1, 12, 'text', _render("_('Retailer')")],
                'lines': [1, 0, 'text', _render("line.so_retailer.name or ''")]
            }
                # 'model_width','model_length','model_gusset', 'model_flap','model_uom','model_quantity','model_unit_price','so_amount','pi_no','so_retailer'
            # 'sale_order_line.product_id': {
            #     'header': [1, 42, 'text', _render("_('Product ID')")],
                # 'lines': [1, 0, 'text', _render("line.product_id.name_template or ''")]
                # },
            # 'unit': {
            #     'header': [1, 20, 'text', _render("_('Unit of measure')")],
            #     # 'lines': [1, 0, 'text', _render("'PCS'")]
            #     },
            # 'product_qty': {
            #     'header': [1, 10, 'text', _render("_('Quantity')"), None, self.rh_cell_style_right],
            #     # 'lines': [1, 0, 'number', _render("line.product_qty")]
            #     },
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list

        _ = _p._

        # report_name = objects[0]._description or objects[0]._name
        report_name = _("Daily Sale Order")
        ws = wb.add_sheet("Daily Sale Order Report")
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        # row_pos INDICATES FROM WHICH ROW THE DATA TABLE WILL START ON EXCEL (TANZIL)
        row_pos = 5

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        for order in objects:
            # Title
            cell_style = xlwt.easyxf(_xs['xls_title'])
            c_specs = [ ('report_name', 1, 0, 'text', report_name+':'+order.date_from) ]
            row_data = self.xls_row_template(c_specs, ['report_name'])
            #row_pos = self.xls_write_row( ws, row_pos, row_data, row_style=cell_style)
            #row_pos += 1
            # Column headers
            c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}),  wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row( ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)

            # HERE IS THE LOOP FOR GETTING VALUE FROM ONE2MANY (TANZIL)
            for line in order.daily_order_rcv_rel:
                c_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'), wanted_list)
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row( ws, row_pos, row_data, row_style=self.aml_cell_style )

            #date romsystems
            font0 = xlwt.Font()
            font0.bold = True
            style0 = xlwt.XFStyle()
            style0.font = font0
            # ws.col(4).width = 500*20
            # ws.col(5).width = 256*25
            ws.write(1, 4, _('DAILY SALE ORDER RECEIVED REPORT'),style0)
            ws.write(2, 4, 'Date For:'+' '+order.date_from,style0)
            ws.write(2, 5, 'Date To:'+' '+order.date_to,style0)
            ws.write(2, 9, 'Total Quantity:',style0)
            ws.write(2, 10, order.total_quantity,style0)
            ws.write(3, 9, 'Total Price:',style0)
            ws.write(3, 10, order.total_amount,style0)
            # ws.write(4, 6, 'CL022842')
            # ws.write(5, 5, 'Mod Livrare',style0)
            # ws.write(6, 5, 'Observatii',style0)
            # if order.notes:
            #     ws.write(6, 6, order.notes)
            # else:
            #     ws.write(6, 6, '')

sale_order_xls('report.sale.order.xls',
              'esq.sale.pi.report',
              parser=sale_order_xls_parser)