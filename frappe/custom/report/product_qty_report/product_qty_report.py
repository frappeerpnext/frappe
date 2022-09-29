# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt


from ast import keyword
from curses import keyname
from tracemalloc import start
import frappe
from datetime import datetime # from python std library
from frappe.utils import add_to_date


def execute(filters=None):

	if filters.get("keyword"):
		keyword = filters.get("keyword").replace("%","")
		if len(keyword)<3:
			frappe.throw("Please enter keyword at lease 3 character")

	report_data =  get_report_data(filters)
	total_record = get_total_record(filters)
	message = ""
	if(total_record>len(report_data)):
		message = "Showing {} of {}. <br/> This report combine with multiple data source and it will loading slowly. Please set filters and limit result to make it loads faster.".format(filters.top, total_record)
	return get_columns(filters),report_data,message

def get_columns(filters):
	columns = get_report_fields(filters)

	return columns

def get_report_data(filters):
	
	sql = "With b as (SELECT DISTINCT parent FROM `tabBranch Items` WHERE branch='{}') SELECT ".format(filters.branch)
	#static column
	for f in get_report_fields(filters):
		sql = sql + " {} as {}, ".format(f["sql_expression"],f["fieldname"])
	sql = sql + "1 as dummy FROM `tabItem` a "
	sql = sql + " Where (a.available_branches='' or a.name in (select parent from b) ) {0} limit {1}".format(get_conditions(filters),filters.top)


	data = frappe.db.sql(sql,filters, as_dict=1)

	return data


def get_total_record(filters):
 
	sql = """
	With b as (SELECT DISTINCT parent FROM `tabBranch Items` WHERE branch='{0}') 
	SELECT 
		count(a.name) as total_record	
	FROM `tabItem` a WHERE (a.available_branches='' or a.name in (select parent from b))  {1} 
	""".format( filters.branch , get_conditions(filters))

	data = frappe.db.sql(sql,filters, as_dict=1)
	total_record = 0
	if data:
		total_record = data[0]["total_record"]
	return total_record 

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data


def get_conditions(filters):

	conditions = ""
	 
	if filters.get("item_group"):
		conditions += " AND a.item_group in %(item_group)s"

	if filters.get("supplier"):
		conditions += " AND a.supplier in %(supplier)s"

	if filters.get("keyword"):
		keyword = filters.get("keyword")
		if '%' in keyword:
			conditions += " AND a.keyword like '{}'".format(keyword.replace("%","%%"))
		else:
			conditions += " AND a.keyword like '%%{}%%'".format(filters.get("keyword"))
  
	return conditions

def get_report_fields(filters):
	fields = [
		{"sql_expression":"a.item_group","fieldname":"item_group","label":"Item Group","fieldtype":"Data","align":"left","width":150},
		{"sql_expression":"if(a.supplier = a.supplier_name,a.supplier,concat(a.supplier,'-',a.supplier_name))","fieldname":"supplier","label":"Supplier","fieldtype":"Data","align":"left","width":150},
		{"sql_expression":"a.item_code","fieldname":"item_code","label":"Item Code","fieldtype":"Data","align":"left","width":100},
		{"sql_expression":"a.item_name","fieldname":"item_name","label":"Item Name","fieldtype":"Data","align":"left","width":250},
		{"sql_expression":"a.stock_uom","fieldname":"stock_uom","label":"Unit","fieldtype":"Data","align":"left","width":75},
	]
	#dynamic field by warehouse
	warehouses = get_warehouses(filters)
	for w in warehouses:
		#reorder level
		if "Reorder Level" in filters.show_columns :
			sql_expression="(SELECT warehouse_reorder_level FROM `tabItem Reorder` r WHERE r.parent = a.item_code   and warehouse='{}')".format(w["name"])
			fieldname ="reorder_level" + w["name"].replace(" ","").replace("-","").lower()
			fields.append({"sql_expression":sql_expression,"fieldname":fieldname,"label":"Re. Lv {}".format(w["warehouse_code"] or w["name"]),"fieldtype":"Data","align":"center","width":120})

		#reorder qty
		if "Reorder Quantity" in filters.show_columns:
			sql_expression="(SELECT warehouse_reorder_qty FROM `tabItem Reorder` r WHERE r.parent = a.item_code   and warehouse='{}')".format(w["name"])
			fieldname = "reorder_qty_" +  w["name"].replace(" ","").replace("-","").lower()
			fields.append({"sql_expression":sql_expression,"fieldname":fieldname,"label":"Re. Qty {}".format(w["warehouse_code"] or w["name"]),"fieldtype":"Data","align":"center","width":120})


		#quantity
		sql_expression="(SELECT coalesce(sum(actual_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse='{}')".format(w["name"])
		fieldname = "qty" + w["name"].replace(" ","").replace("-","").lower()
		fields.append({"sql_expression":sql_expression,"fieldname":fieldname,"label":"Qty {}".format(w["warehouse_code"] or w["name"]),"fieldtype":"Data","align":"center","width":120})

		#reserved quantity
		if "Reserved Quantity" in filters.show_columns:
			sql_expression="(SELECT coalesce(sum(reserved_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse='{}')".format(w["name"])
			fieldname = "reserved_qty_" +  w["name"].replace(" ","").replace("-","").lower()
			fields.append({"sql_expression":sql_expression,"fieldname":fieldname,"label":"Reserved Qty {}".format(w["warehouse_code"] or w["name"]),"fieldtype":"Data","align":"center","width":120})

		#order  quantity
		if "Ordered Quantity" in filters.show_columns:
			sql_expression="(SELECT coalesce(sum(ordered_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse='{}')".format(w["name"])
			fieldname = "order_qty_" +  w["name"].replace(" ","").replace("-","").lower()
			fields.append({"sql_expression":sql_expression,"fieldname":fieldname,"label":"Ordered Qty {}".format(w["warehouse_code"] or w["name"]),"fieldtype":"Data","align":"center","width":120})

		#requested quajtity
		if "Requested Quantity" in filters.show_columns:
			sql_expression="(SELECT coalesce(sum(indented_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse='{}')".format(w["name"])
			fieldname = "requested_qty_" +  w["name"].replace(" ","").replace("-","").lower()
			fields.append({"sql_expression":sql_expression,"fieldname":fieldname,"label":"Req. Qty {}".format(w["warehouse_code"] or w["name"]),"fieldtype":"Data","align":"center","width":120})

	str_warehouses   = ','.join("'{0}'".format(x["name"]) for x in warehouses)
	#get total column
	if len(warehouses)>1:
		#total qty column 
		sql_expression="(SELECT coalesce(sum(actual_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse in ({}))".format(str_warehouses)
		fields.append({"sql_expression":sql_expression,"fieldname":"total_qty","label":"Total Qty","fieldtype":"Data","align":"center","width":120})

		#reserved quantity
		if "Reserved Quantity" in filters.show_columns:
			sql_expression="(SELECT coalesce(sum(reserved_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse in ({}))".format(str_warehouses)
			fields.append({"sql_expression":sql_expression,"fieldname":"total_reserved_quantity","label":"Total Resv. Qty","fieldtype":"Data","align":"center","width":120})

		#order  quantity
		if "Ordered Quantity" in filters.show_columns:
			sql_expression="(SELECT coalesce(sum(ordered_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse in ({}))".format(str_warehouses)
			fields.append({"sql_expression":sql_expression,"fieldname":"total_order_quantity","label":"Total Ordered Qty","fieldtype":"Data","align":"center","width":120})

		#requested quajtity
		if "Requested Quantity" in filters.show_columns:
			sql_expression="(SELECT coalesce(sum(indented_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse in ({}))".format(str_warehouses)
			fields.append({"sql_expression":sql_expression,"fieldname":"total_request_quantity","label":"Total Req. Qty","fieldtype":"Data","align":"center","width":120})

	#requested quajtity
	if "Requested Quantity" in filters.show_columns:
		sql_expression="(SELECT coalesce(sum(indented_qty),0) FROM `tabBin` f WHERE f.item_code = a.item_code AND f.stock_uom = a.stock_uom and warehouse in ({}))".format(str_warehouses)
		fields.append({"sql_expression":sql_expression,"fieldname":"total_request_quantity","label":"Total Req. Qty","fieldtype":"Data","align":"center","width":120})
	if "Quantity Sold" in filters.show_columns:
		sql_expression = "(select sum(x.qty*x.conversion_factor) from `tabSales Invoice Item` x inner join `tabSales Invoice` y on y.name = x.parent where a.name = x.item_code and  y.docstatus in (1) and y.set_warehouse in ({}) and y.posting_date between '{}' and '{}')".format(str_warehouses,filters.start_date,filters.end_date)
		fields.append({"sql_expression":sql_expression,"fieldname":"sold_qty","label":"Sold","fieldtype":"Data","align":"center","width":120})
	#Qty Purchase Yesterday
	if "Quantity Purchase" in filters.show_columns:
		sql_expression = "(select sum(x.qty*x.conversion_factor) from `tabPurchase Order Item` x inner join `tabPurchase Order` y on y.name = x.parent where a.name = x.item_code and  y.docstatus in (1) and y.set_warehouse in ({}) and y.transaction_date between '{}' and '{}')".format(str_warehouses,filters.start_date,filters.end_date)
		fields.append({"sql_expression":sql_expression,"fieldname":"purchase_qty","label":"Purchase","fieldtype":"Data","align":"center","width":120})
	#Qty receive Yesterday
	if "Quantity Receive" in filters.show_columns:
		sql_expression = "(select sum(x.actual_qty) from `tabStock Ledger Entry` x  where a.name = x.item_code and  x.voucher_type in ('Purchase Receipt','Stock Entry') and x.warehouse in ({}) and x.posting_date between '{}' and '{}')".format(str_warehouses,filters.start_date,filters.end_date)
		fields.append({"sql_expression":sql_expression,"fieldname":"receive_qty","label":"Received","fieldtype":"Data","align":"center","width":120})
	return fields

def get_warehouses(filters):
	if filters.get("warehouse"):
		return frappe.db.get_list("Warehouse",filters=[{"name":["in",filters.get("warehouse")]}],fields=["name","warehouse_code"])
	warehouses =   frappe.db.get_list("Warehouse",fields=["name","warehouse_code"])
	
 
	return warehouses

def get_warehouse_conditions(filters):
	conditions = ""
	conditions += " AND f.warehouse = %(warehouse)s"
 
	return conditions