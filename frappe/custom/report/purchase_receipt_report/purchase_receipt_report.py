# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

from dataclasses import dataclass
from unittest.mock import MagicMixin
import frappe


def execute(filters=None):
	
	return get_columns(filters),get_data(filters)

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'name','label':"Purchase Receipt",'fieldtype':'Data','align':'left','width':300})
	columns.append({'fieldname':'company','label':"Company",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'set_warehouse','label':"Warehouse",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'posting_date','label':"Date",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'qty','label':"Total QTY",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'amount','label':"Amount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'status','label':"Status",'fieldtype':'Data','align':'right','width':150})
	return columns

def get_data(filters):
	data=[]
	parent = """
				SELECT
					supplier_name name,
					supplier,
					SUM(total_qty) qty,
					SUM(net_total) amount
				FROM `tabPurchase Receipt` a
					WHERE {}
				GROUP BY
					supplier,
					supplier_name
			""".format(get_filters(filters))
	parent_data = frappe.db.sql(parent,as_dict=1)
	for dic_p in parent_data:
		dic_p["indent"] = 0
		dic_p["is_group"] = 1
		data.append(dic_p)
		child_data = ("""
						SELECT
							name,
							supplier,
							supplier_name,
							posting_date,
							SUM(total_qty) qty,
							SUM(net_total) amount,
							status,
							company,
							set_warehouse
						FROM `tabPurchase Receipt` a
						WHERE {0} and supplier = '{1}'
						GROUP BY
							name,
							supplier,
							supplier_name,
							posting_date,
							status,
							company,
							set_warehouse
					""".format(get_filters(filters),dic_p["supplier"]))
		child = frappe.db.sql(child_data,as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)
	return data

def get_filters(filters):
	data= "posting_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	if filters.get("supplier"):data = data +	" and supplier in (" + get_list(filters,"supplier") + ")"
	if filters.get("supplier_group"):data = data +	" and (SELECT supplier_group FROM `tabSupplier` b WHERE b.name = a.supplier) in (" + get_list(filters,"supplier_group") + ")"
	if filters.get("status"):data = data +	" and status in (" + get_list(filters,"status") + ")"
	if filters.get("company"):data = data +	" and company in (" + get_list(filters,"company") + ")"
	if filters.get("warehouse"):data = data +	" and set_warehouse in (" + get_list(filters,"warehouse") + ")"
	return data


def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data