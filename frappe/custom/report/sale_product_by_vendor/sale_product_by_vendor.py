# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_filters(filters):
	data= "b.docstatus=1 and b.posting_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	if filters.get("company"): data = data + " and b.company = '{}'".format(filters.company)
	if filters.get("supplier"):data = data +	" and a.supplier in (" + get_list(filters,"supplier") + ")"
	if filters.get("branch"):data = data +	" and b.branch in (" + get_list(filters,"branch") + ")"
	if filters.get("warehouse"): data = data + " and a.warehouse = '{}'".format(filters.warehouse)
	if filters.get("not_set_supplier"): data = data + " and a.supplier_name is null"
	if filters.get("item_group"):data = data +	" and (coalesce(a.parent_item_group,(SELECT parent_item_group FROM `tabItem Group` WHERE NAME = a.item_group)) in (" + get_list(filters,"item_group") + ")" + " or a.item_group in (" + get_list(filters,"item_group") + "))"
	if filters.get("item_category"):data = data +	" and a.item_group in (" + get_list(filters,"item_category") + ")"
	if filters.get("supplier_group"):data = data +	" and (SELECT supplier_group FROM `tabSupplier` b WHERE b.name = a.supplier) in (" + get_list(filters,"supplier_group") + ")"
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'supplier','label':"Supplier",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_category','label':"Category",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_code','label':"Item Code",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'item_name','label':"Item Name",'fieldtype':'Data','align':'left','width':350})
	columns.append({'fieldname':'branch','label':"Branch",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'stock_uom','label':"Unit",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'sale_qty','label':"Sale",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'warehouse','label':"Warehouse",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'boh','label':"BOH",'fieldtype':'Data','align':'right','width':100})
	return columns

def get_data(filters):
	data=[]
	parent = """
				SELECT 
					coalesce(supplier,'Not Set') supplier,
					coalesce(supplier_name,'Not Set') supplier_name
				FROM `tabSales Invoice Item` a
					INNER JOIN `tabSales Invoice` b ON b.name = a.parent
				WHERE {0}
					GROUP BY a.supplier
			""".format(get_filters(filters),filters.start_date,filters.end_date,filters.warehouse)
	parent_data = frappe.db.sql(parent,as_dict=1)
	for dic_p in parent_data:
		dic_p["indent"] = 0
		dic_p["is_group"] = 1
		data.append(dic_p)
		child_data = ("""
						SELECT
							a.parent_item_group supplier,
							coalesce(a.item_group,'Not Set') item_category,
							a.item_code,
							a.item_name,
							a.stock_uom,
							coalesce(SUM(coalesce(a.qty,0) * coalesce(a.conversion_factor,0)),0) sale_qty,
							coalesce((SELECT sum(coalesce(actual_qty,0)) FROM `tabBin` c where c.item_code = a.item_code and c.warehouse = a.warehouse),0) boh,
							a.warehouse,
							b.branch
						FROM `tabSales Invoice Item` a
							INNER JOIN `tabSales Invoice` b ON b.name = a.parent									
						WHERE {0} and coalesce(a.supplier,'Not Set') = '{4}'
						GROUP BY
							a.parent_item_group,
							a.item_group,
							a.item_code,
							a.item_name,
							a.stock_uom,
							a.warehouse,
							b.branch
					""".format(get_filters(filters),filters.start_date,filters.end_date,filters.warehouse,dic_p["supplier"]))
		child = frappe.db.sql(child_data,as_dict=1)
		temp=[]
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)
			temp.append(dic_c)
		data.append({"sale_qty": sum(c.sale_qty for c in temp), "boh": sum(c.boh for c in temp), "last_row": 1})
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data