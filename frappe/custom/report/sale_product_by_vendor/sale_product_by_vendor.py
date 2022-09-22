# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_filters(filters):
	data= "b.posting_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	if filters.get("company"): data = data + " and b.company = '{}'".format(filters.company)
	if filters.get("supplier"):data = data +	" and c.supplier_name in (" + get_list(filters,"supplier") + ")"
	if filters.get("warehouse"): data = data + " and a.warehouse = '{}'".format(filters.warehouse)
	if filters.get("not_set_supplier"): data = data + " and c.supplier_name is null"
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'item_code','label':"Item Code",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'item_name','label':"Item Name",'fieldtype':'Data','align':'left','width':350})
	columns.append({'fieldname':'supplier_name','label':"Supplier",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'stock_uom','label':"Unit",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'boh','label':"BOH",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'sale_qty','label':"Sale",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'total_qty','label':"Total BOH",'fieldtype':'Data','align':'right','width':100})
	return columns

def get_data(filters):
	data=[]
	parent = """
				with sale as(SELECT
									c.item_group, 
									coalesce(c.supplier_name,'Not Set') supplier_name,
									a.item_code,
									a.item_name,
									a.stock_uom,
									coalesce(SUM(a.qty * a.conversion_factor),0) sale_qty
								FROM `tabSales Invoice Item` a
									INNER JOIN `tabSales Invoice` b ON b.name = a.parent
									INNER JOIN `tabItem` c ON c.item_code = a.item_code										
								WHERE {0}
								GROUP BY
									c.item_group, 
									c.supplier_name,
									a.item_code,
									a.item_name,
									a.stock_uom)
								SELECT
								c.item_group item_code,
								COUNT(DISTINCT(c.item_code)) item_name,
								sum(c.sale_qty) sale_qty,
								SUM((SELECT 
										qty_after_transaction
										FROM  `tabStock Ledger Entry` a
										WHERE  concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')) =
										( SELECT  max(concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')))
												FROM  `tabStock Ledger Entry` b
												WHERE posting_date BETWEEN '{1}' AND '{2}' and b.item_code = a.item_code AND b.warehouse = if('{3}'='None',b.warehouse,'{3}')
										)
									and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = if('{3}'='None',warehouse,'{3}') AND a.item_code = c.item_code)) boh,
								SUM((SELECT 
										qty_after_transaction
										FROM  `tabStock Ledger Entry` a
										WHERE  concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')) =
										( SELECT  max(concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')))
												FROM  `tabStock Ledger Entry` b
												WHERE posting_date BETWEEN '{1}' AND '{2}' and b.item_code = a.item_code AND b.warehouse = if('{3}'='None',b.warehouse,'{3}')
										)
									and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = if('{3}'='None',warehouse,'{3}') AND a.item_code = c.item_code) - c.sale_qty) total_qty
								FROM sale c
								GROUP BY item_group
			""".format(get_filters(filters),filters.start_date,filters.end_date,filters.warehouse)
	parent_data = frappe.db.sql(parent,as_dict=1)
	for dic_p in parent_data:
		dic_p["indent"] = 0
		dic_p["is_group"] = 1
		data.append(dic_p)
		child_data = ("""
						with sale as(SELECT
							c.item_group, 
							coalesce(c.supplier_name,'Not Set') supplier_name,
							a.item_code,
							a.item_name,
							a.stock_uom,
							coalesce(SUM(a.qty * a.conversion_factor),0) sale_qty
						FROM `tabSales Invoice Item` a
							INNER JOIN `tabSales Invoice` b ON b.name = a.parent
							INNER JOIN `tabItem` c ON c.item_code = a.item_code										
						WHERE {0} and c.item_group = '{3}'
						GROUP BY
							c.item_group, 
							c.supplier_name,
							a.item_code,
							a.item_name,
							a.stock_uom)
						SELECT
						c.*,
						(SELECT 
								qty_after_transaction
								FROM  `tabStock Ledger Entry` a
								WHERE  concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')) =
								( SELECT  max(concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')))
										FROM  `tabStock Ledger Entry` b
										WHERE posting_date BETWEEN '{1}' AND '{2}' and b.item_code = a.item_code AND b.warehouse = if('{4}'='None',b.warehouse,'{4}')
								)
							and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = if('{4}'='None',warehouse,'{4}') AND a.item_code = c.item_code) boh,
						(SELECT 
								qty_after_transaction
								FROM  `tabStock Ledger Entry` a
								WHERE  concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')) =
								( SELECT  max(concat(posting_date,' ',time_format(creation,'%H:%i:%s.%f')))
										FROM  `tabStock Ledger Entry` b
										WHERE posting_date BETWEEN '{1}' AND '{2}' and b.item_code = a.item_code AND b.warehouse = if('{4}'='None',b.warehouse,'{4}')
								)
							and posting_date BETWEEN '{1}' AND '{2}' AND warehouse = if('{4}'='None',warehouse,'{4}') AND a.item_code = c.item_code) - c.sale_qty total_qty
						FROM sale c
					""".format(get_filters(filters),filters.start_date,filters.end_date,dic_p["item_code"],filters.warehouse))
		child = frappe.db.sql(child_data,as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data