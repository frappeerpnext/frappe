# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return get_columns(filters), get_report_data(filters)

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'item_group','label':"Item Group",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'supplier','label':"Supplier",'fieldtype':'Data','align':'left','width':180	})
	columns.append({'fieldname':'item_code','label':"Barcode",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'item_name','label':"Description",'fieldtype':'Data','align':'left'})
	columns.append({'fieldname':'actual_qty','label':"QTY",'fieldtype':'Data','align':'center','width':70})
	return columns

def get_report_data(filters):
 
	sql = """
	SELECT 
		a.item_group,
		a.item_code,
		if(a.supplier = a.supplier_name,a.supplier,concat(a.supplier,'-',a.supplier_name)) as supplier,
		a.item_name,
		a.stock_uom,
		coalesce((SELECT GROUP_CONCAT(branch SEPARATOR ', ') FROM `tabBranch Items` g WHERE g.parent = a.item_code GROUP BY g.parent),"All") available_branch,
		(SELECT coalesce(sum(actual_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom {0}) actual_qty
	FROM `tabItem` a WHERE 1=1  {1}
	""".format(get_warehouse_conditions(filters),get_conditions(filters))


 

	data = frappe.db.sql(sql,filters, as_dict=1)

	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data


def get_conditions(filters):

	conditions = ""
	 
	if filters.get("item_group"):
		conditions += " AND a.item_group in %(item_group)s"

	if filters.get("supplier"):
		conditions += " AND a.supplier in %(supplier)s"
  
	return conditions

def get_warehouse_conditions(filters):
	conditions = ""
	if filters.get("warehouse"):
		conditions += " AND f.warehouse in %(warehouse)s"
 
	return conditions