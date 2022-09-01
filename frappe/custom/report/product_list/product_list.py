# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return get_columns(filters), get_report_data(filters)

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'item_group','label':"Item Group",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_code','label':"Barcode",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_name','label':"Description",'fieldtype':'Data','align':'left','width':100})
	columns.append({'fieldname':'actual_qty','label':"Unit",'fieldtype':'Data','align':'left','width':70})
	columns.append({'fieldname':'allow_discount','label':"Allow Discount",'fieldtype':'Currency','align':'left','width':100})
	return columns
def get_report_data(filters):
	sql = """
	SELECT 
		a.item_group,
		a.item_code,
		a.item_name,
		a.stock_uom,
		(SELECT actual_qty FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom AND warehouse = '{0}') price,
		(SELECT price_list_rate FROM `tabItem Price` c WHERE item_code = a.item_code AND c.uom = a.stock_uom AND price_list = 'Standard Selling') price,
		(SELECT price_list_rate FROM `tabItem Price` d WHERE item_code = a.item_code AND d.uom = a.stock_uom AND price_list = 'Wholesale Price') whole_sale,
		(SELECT price_list_rate FROM `tabItem Price` e WHERE item_code = a.item_code AND e.uom = a.stock_uom AND price_list = 'Standard Buying'),
		a.allow_discount
	FROM `tabItem` a WHERE a.item_group = '{1}' AND a.allow_discount = '{2}'
	""".format(filters.warehouse, filters.item_group,filters.allow_discount)

	data = frappe.db.sql(sql,as_dict=1)
	return data