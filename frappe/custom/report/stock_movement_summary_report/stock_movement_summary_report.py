# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import data
def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_date(filters):
	con = "a.posting_date BETWEEN '{0}' AND '{1}'".format(filters.start_date,filters.end_date)
	return con

def start_date(filters):
	con = "'{0}'".format(filters.start_date)
	return con

def get_item_filter(filters):
	con = ""
	if filters.get("item_group"):con = con + " and coalesce(b.item_group,'Not Set') in (" + get_list(filters,"item_group") + ")"
	if filters.get("supplier"):con = con + " and coalesce(b.supplier,'Not Set') in (" + get_list(filters,"supplier") + ")"
	return con

def get_filter(filters):
	con = "where 1=1"
	if filters.get("brand"):con = con + " and coalesce(a.brand,'Not Set') in (" + get_list(filters,"brand") + ")"
	if filters.get("show_not_set") == 1:con = con + " and a.brand is null" 
	return con

def get_data(filters):
	sql = """
		WITH sle AS( SELECT 
		a.item_code,
		item_name,
		b.brand,
		b.stock_uom
		FROM `tabStock Ledger Entry` a
		INNER JOIN `tabItem` b ON b.name = a.item_code
		WHERE {0} {2} and is_cancelled=0
		GROUP BY 
		a.item_code,
		item_name)
		,sale AS (
		SELECT 
		item_code,
		SUM(qty) sale_qty
		FROM `tabSales Invoice` a
		INNER JOIN `tabSales Invoice Item` b ON b.parent = a.name
		WHERE {0} and a.docstatus=1 AND b.docstatus=1
		GROUP BY b.item_code)
		,purchase AS(
		SELECT 
		item_code,
		SUM(qty) purchase_qty
		FROM `tabPurchase Receipt` a
		INNER JOIN `tabPurchase Receipt Item` b ON b.parent = a.name
		WHERE {0} and a.docstatus=1 AND b.docstatus=1
		GROUP BY b.item_code)
		,reconciliation AS (
		SELECT 
		item_code,
		SUM(quantity_difference) reconciliation_qty
		FROM `tabStock Reconciliation` a
		INNER JOIN `tabStock Reconciliation Item` b ON b.parent = a.name
		WHERE {0} and a.docstatus=1 AND b.docstatus=1
		GROUP BY b.item_code)
		SELECT 
		a.item_code,
		a.item_name,
		coalesce(a.brand,'Not Set') brand,
		a.stock_uom,
		coalesce(b.sale_qty,0) sale_qty,
		coalesce(c.purchase_qty,0) purchase_qty,
		COALESCE(d.reconciliation_qty,0) reconciliation_qty,
		COALESCE(get_last_row_qty(a.item_code,{3}),0) start_qty,
		COALESCE(get_last_row_qty(a.item_code,{3}),0) - b.sale_qty + coalesce(c.purchase_qty,0) + COALESCE(d.reconciliation_qty,0) end_qty
		FROM sle a
		LEFT JOIN sale b ON b.item_code = a.item_code
		LEFT JOIN purchase c ON c.item_code = a.item_code
		LEFT JOIN reconciliation d ON d.item_code = a.item_code
		{1}
	""".format(get_date(filters),get_filter(filters),get_item_filter(filters),start_date(filters))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'item_code','label':"Item Code",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'item_name','label':"Item Name",'fieldtype':'Data','align':'left','width':250})
	columns.append({'fieldname':'brand','label':"Brand",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'stock_uom','label':"UOM",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'start_qty','label':"Beginning QTY",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'sale_qty','label':"Sale",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'purchase_qty','label':"Purchase",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'reconciliation_qty','label':"Adjust Stock",'fieldtype':'Data','align':'right','width':100})
	columns.append({'fieldname':'end_qty','label':"Last QTY",'fieldtype':'Data','align':'right','width':100})
	return columns


def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data