# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe


from frappe import msgprint
import frappe


def execute(filters=None):
	
	message = "We limit report to 50 record to load report faster. If you want to show all record set Show Record = 0"
	
	#run sql statement to update parent item group if it blank
	update_blank_parent_item_group()

	return get_columns(filters),get_report_data(filters),message, None,get_report_summary(filters)

def get_columns(filters):
	columns = []
	show_columns= filters.get("show_columns")

	columns.append({'fieldname':'item_group','label':"Category",'fieldtype':'Data','align':'left','width':250})
	columns.append({'fieldname':'item_name','label':"Item Name",'fieldtype':'Data','align':'left','width':250})
	columns.append({'fieldname':'stock_uom','label':"Unit",'fieldtype':'Data','align':'left'})
	warehouses = get_warehouses(filters)
	for w in warehouses:
		columns.append({'fieldname':"actual_qty_" + w["warehouse"],'label':"Actual Qty <br/>" + w["warehouse_name"],'fieldtype':'Float','align':'center','precision': 2})
		
		if show_columns and "Reserved Quantity"  in show_columns:
			columns.append({'fieldname':"reserved_qty_" + w["warehouse"],'label':"Reserved Qty <br/>" + w["warehouse_name"],'fieldtype':'Float','align':'center','precision': 2})
		
		if show_columns and "Ordered Quantity"  in show_columns:
			columns.append({'fieldname':"ordered_qty_" + w["warehouse"],'label':"Ordered Qty <br/>" + w["warehouse_name"],'fieldtype':'Float','align':'center','precision': 2})

		if show_columns and "Requested Quantity"  in show_columns:
			columns.append({'fieldname':"requested_qty_" + w["warehouse"],'label':"Requested Qty <br/>" + w["warehouse_name"],'fieldtype':'Float','align':'center','precision': 2})

		if show_columns and "Total Cost"  in show_columns:
			columns.append({'fieldname':"total_cost_" + w["warehouse"],'label':"Total Cost <br/>" + w["warehouse_name"],'fieldtype':'Currency','align':'right'})

		

	if len(warehouses)>1:
		columns.append({'fieldname':"total_actual_qty",'label':" Total Actual Qty",'fieldtype':'Float','align':'center','precision': 2})
		if show_columns and "Reserved Quantity"  in show_columns:
			columns.append({'fieldname':"total_reserved_qty",'label':"Total Reserved Qty",'fieldtype':'Float','align':'center','precision': 2})
		
		if show_columns and "Ordered Quantity"  in show_columns:
			columns.append({'fieldname':"total_ordered_qty",'label':"Total Ordered Qty",'fieldtype':'Float','align':'center','precision': 2})
		
		if show_columns and "Requested Quantity"  in show_columns:
			columns.append({'fieldname':"total_requested_qty",'label':"Total Requested Qty",'fieldtype':'Float','align':'center','precision': 2})

		if show_columns and "Total Cost"  in show_columns:
			columns.append({'fieldname':"total_cost",'label':"Total Cost",'fieldtype':'Currency','align':'center'})

	return columns

def get_report_data(filters):
	show_columns = filters.get("show_columns")
	limit = filters.limit
	if  not filters.limit or filters.limit == 0:
		limit = 10000000

	sql = """
		select 
			 
			a.item_group,
			concat(a.item_code,'-',a.item_name) as item_name,
			a.stock_uom
	"""
	warehouses = get_warehouses(filters)
	for w in warehouses:
		sql = sql + ",sum(if(warehouse='{}',a.actual_qty,0)) as actual_qty_{}".format(w["warehouse_name"],w["warehouse"])
		if show_columns and "Reserved Quantity"  in show_columns:
			sql = sql + ",sum(if(warehouse='{}',a.reserved_qty,0)) as reserved_qty_{}".format(w["warehouse_name"],w["warehouse"])
		
		if show_columns and "Ordered Quantity"  in show_columns:
			sql = sql + ",sum(if(warehouse='{}',a.ordered_qty,0)) as ordered_qty_{}".format(w["warehouse_name"],w["warehouse"])

		if show_columns and "Requested Quantity"  in show_columns:
			sql = sql + ",sum(if(warehouse='{}',a.indented_qty,0)) as requested_qty_{}".format(w["warehouse_name"],w["warehouse"])
		
		if show_columns and "Total Cost"  in show_columns:
			sql = sql + ",sum(if(warehouse='{}',a.stock_value,0)) as total_cost_{}".format(w["warehouse_name"],w["warehouse"])

	#total column
	if len(warehouses)>1:
		sql = sql + ",sum(a.actual_qty) as total_actual_qty"

		if show_columns and "Reserved Quantity"  in show_columns:
			sql = sql + ",sum(a.reserved_qty) as total_reserved_qty"
		if show_columns and "Ordered Quantity"  in show_columns:
			sql = sql + ",sum(a.ordered_qty) as total_ordered_qty"
		if show_columns and "Requested Quantity"  in show_columns:
			sql = sql + ",sum(a.indented_qty) as total_requested_qty"
		if show_columns and "Total Cost"  in show_columns:
			sql = sql + ",sum(a.stock_value) as total_cost"

	sql = sql + """			
		from 
		`tabBin` a
		where 
			1 = 1  
			{0}
		group by
			a.item_group,
			concat(a.item_code,'-',a.item_name),
			a.stock_uom
		limit {1}
	""".format(get_conditions(filters), limit)

	data = frappe.db.sql(sql,filters,as_dict=1)

	
	return data


def get_conditions(filters):
	conditions = ""
	
	if filters.get("item_group"):
		conditions += " AND a.parent_item_group in %(item_group)s "
	
	if filters.get("item_category"):
		conditions += " AND a.item_group in %(item_category)s "
	
	if filters.get("warehouse"):
		conditions += " AND a.warehouse in %(warehouse)s "
	
	if filters.get("company"):
		conditions += " AND a.company  =  %(company)s "

	return conditions


def get_report_summary(filters):
  
	report_summary =[{"label":"Total Qty " ,"value":50,'indicator':'grey'}]

	 

	#if not hide_columns or  "Profit" not in hide_columns:
	#	report_summary.append({"label":"Total Profit","value":frappe.utils.fmt_money(sum(d["total_profit"] for d in data)),'indicator':'#FF3D00'})

 
	return report_summary
	
def update_blank_parent_item_group():
	frappe.db.sql("""
		update `tabBin` a 
		set parent_item_group = (select parent_item_group from `tabItem Group` b where b.name=a.item_group)
		where 
			ifnull(parent_item_group,'') = ''
	""")

def get_warehouses(filters):
	sql = """
		select 
			distinct 
			replace(warehouse,' - ','') as warehouse,
			warehouse as warehouse_name
		from 
		`tabBin` a
	"""
	if filters.get("warehouse"):
		sql = sql + """
			 where
			a.warehouse in %(warehouse)s
		"""
	data = frappe.db.sql(sql,filters,as_dict=1)
	 
	return data