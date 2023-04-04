# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_filters(filters):
	data = "where "
	if filters.get("company"): data = data + "a.company_name = '{}'".format(filters.company)
	if filters.get("balance"): data = data + "and a.actual_qty {}".format(filters.balance)
	if filters.get("supplier"):data = data +	" and b.supplier in (" + get_list(filters,"supplier") + ")"
	if filters.get("supplier_group"):data = data +	" and c.supplier_group in (" + get_list(filters,"supplier_group") + ")"
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'supplier_group','label':"Supplier Group",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'supplier_name','label':"Supplier",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_code','label':"Item Code",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_name','label':"Item Name",'fieldtype':'Data','align':'left','width':400})
	columns.append({'fieldname':'stock_uom','label':"UOM",'fieldtype':'Data','align':'left','width':80})
	columns.append({'fieldname':'actual_qty','label':"BOH",'fieldtype':'Data','align':'left','width':80})
	return columns

def get_data(filters):
	data=[]
	sql = """
			SELECT 
				a.item_code,
				a.item_name,
				a.actual_qty,
				a.stock_uom,
				coalesce(b.supplier_name ,'Not Set') supplier_name,
				COALESCE(c.supplier_group ,'Not Set') supplier_group
			FROM `tabBin` a
			INNER JOIN `tabItem` b ON b.name = a.item_code
			left JOIN `tabSupplier` c ON c.name = b.supplier
			{0}
			""".format(get_filters(filters))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data