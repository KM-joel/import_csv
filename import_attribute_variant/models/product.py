import csv
import logging
from odoo import Command, models

_logger = logging.getLogger(__name__)


class ProductAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    def import_attribute_line(self):
        csv_file = '/opt/Copie_de_attributes_data_1.csv'
        try:
            with open(csv_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=',')
                for row in reader:
                    modified_row = {}
                    for key, value in row.items():
                        if key == 'id externe':
                            val = value.split('_')
                            prod_templ = self.env['product.template'].search([
                                ('active', '=?', False), ('id_externe', '=', val[1])
                            ])
                            modified_row['product_tmpl_id'] = prod_templ  # self.env.ref(str(value))

                        if key == 'attribute_line_ids/attribute_id/id':
                            modified_row['attribute_id'] = self.env.ref(str(value))
                        if key == 'attribute_line_ids/value_ids/id':
                            modified_row['value_ids'] = self.env.ref(str(value))

                    if modified_row.get('product_tmpl_id') and modified_row.get('attribute_id') and modified_row.get('value_ids'):
                        product_tmpl_id = modified_row.get('product_tmpl_id')
                        # domain = [('attribute_id', '=', modified_row.get('attribute_id').id)]
                        lines = product_tmpl_id.attribute_line_ids.filtered(lambda li: li.attribute_id.id == modified_row.get('attribute_id').id)
                        if product_tmpl_id.attribute_line_ids and lines:
                            _logger.info(f"=>>>>> Exist values : {product_tmpl_id.attribute_line_ids.mapped('value_ids')}")
                            for line in lines:
                                line.value_ids = [Command.link(modified_row.get('value_ids').id)]
                            _logger.info(f"=>>>>> product name : {product_tmpl_id.name}")
                            _logger.info(f"=>>>>> Exist values : {product_tmpl_id.attribute_line_ids.mapped('value_ids')}")

                        elif not product_tmpl_id.attribute_line_ids or not lines:
                            vals = {
                                'product_tmpl_id': product_tmpl_id.id,
                                'attribute_id': modified_row.get('attribute_id').id,
                                'value_ids': [Command.set([modified_row.get('value_ids').id])],
                            }
                            _logger.info(f"=>>>>> line : {product_tmpl_id.attribute_line_ids}")
                            product_tmpl_id.attribute_line_ids = [Command.create(vals)]
                            _logger.info(f"=>>>>> product name : {product_tmpl_id.name}")
                            _logger.info(f"=>>>>> line : {product_tmpl_id.attribute_line_ids}")

        except Exception as exc:
            _logger.error(f"=>>>>> : {exc}")
