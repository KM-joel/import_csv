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
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    modified_row = {}
                    for key, value in row.items():
                        if key == 'ID externe':
                            modified_row['product_tmpl_id'] = self.env.ref(str(value))
                        if key == 'attribute_line_ids/id':
                            modified_row['line'] = self.env.ref(str(value))
                        if key == 'attribute_line_ids/attribute_id/id':
                            modified_row['attribute_id'] = self.env.ref(str(value))
                        if key == 'attribute_line_ids/value_ids/id':
                            modified_row['value_ids'] = self.env.ref(str(value))

                    if modified_row.get('product_tmpl_id') and modified_row.get('line') and modified_row.get('attribute_id') and modified_row.get('value_ids'):
                        product_tmpl_id = self.env['product.template'].browse(modified_row.get('product_tmpl_id').id)
                        _logger.error(f"=>>>>> product name : {product_tmpl_id.name}")
                        domain = [
                            ('id', '=', modified_row.get('line').id),
                            ('attribute_id', '=', modified_row.get('attribute_id').id)
                        ]
                        if not product_tmpl_id.attribute_line_ids or not product_tmpl_id.attribute_line_ids.search(domain):
                            vals = {
                                'attribute_id': modified_row.get('attribute_id').id,
                                'value_ids': [Command.set([modified_row.get('value_ids').id])],
                            }
                            product_tmpl_id.attribute_line_ids = [Command.create(vals)]

                        if product_tmpl_id.attribute_line_ids and product_tmpl_id.attribute_line_ids.search(domain):
                            for line in product_tmpl_id.attribute_line_ids.search(domain):
                                line.value_ids = [Command.link(modified_row.get('value_ids').id)]

        except Exception as exc:
            _logger.error(f"=>>>>> : {exc}")
