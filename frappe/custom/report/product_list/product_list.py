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
	warehouse = ""
	item_group = ""
	if filters.get("warehouse"): warehouse = "and a.warehouse in (" + get_list(filters,"warehouse") + ")"
	if filters.get("item_group"): item_group = "a.item_group in (" + get_list(filters,"item_group") + ") and"
	sql = """
	SELECT 
		a.item_group,
		a.item_code,
		a.item_name,
		a.stock_uom,
		(SELECT sum(actual_qty) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom {0}) price,
		(SELECT price_list_rate FROM `tabItem Price` c WHERE item_code = a.item_code AND c.uom = a.stock_uom AND price_list = 'Standard Selling') price,
		(SELECT price_list_rate FROM `tabItem Price` d WHERE item_code = a.item_code AND d.uom = a.stock_uom AND price_list = 'Wholesale Price') whole_sale,
		(SELECT price_list_rate FROM `tabItem Price` e WHERE item_code = a.item_code AND e.uom = a.stock_uom AND price_list = 'Standard Buying') cost,
		a.allow_discount
	FROM `tabItem` a WHERE {1} a.allow_discount = if('{2}'='All',a.allow_discount,if('{2}'='Yes',1,0))
	""".format(warehouse, item_group,filters.allow_discount)
	frappe.msgprint("<pre>{}</pre>".format(sql))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data