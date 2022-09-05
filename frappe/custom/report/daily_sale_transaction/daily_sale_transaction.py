# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
def execute(filters=None):
	get_data=[]
	get_column=[]
	if filters.group_by == 'Customer' : get_data = get_report_data1(filters);get_column=get_columns_by_customer(filters)
	if filters.group_by == 'Document #' : get_data = get_report_data(filters);get_column=get_columns(filters)
	return get_column, get_data 

def get_filters(filters):
	con = "b.posting_date BETWEEN '{0}' AND '{1}' AND b.company = '{2}' and a.docstatus=1 and b.docstatus=1".format(filters.start_date,filters.end_date,filters.company)
	if filters.get("price_list"): con = con + " and b.selling_price_List in (" + get_list(filters,"price_list") + ")"
	if filters.get("customer"):con = con +	" and b.customer in (" + get_list(filters,"customer") + ")"
	return con

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'parent','label':"Document #",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'posting_date','label':"Date",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'customer','label':"Customer",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'qty','label':"QTY",'fieldtype':'Data','align':'center','width':70})
	columns.append({'fieldname':'cost','label':"Cost",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'sub_total','label':"Sub Total",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'discount','label':"Discount",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'grand_total','label':"Amount",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'profit','label':"Profit",'fieldtype':'Currency','align':'right','width':100})
	return columns

def get_columns_by_customer(filters):
	columns = []
	columns.append({'fieldname':'customer','label':"Customer",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'parent','label':"Document #",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'posting_date','label':"Date",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'qty','label':"QTY",'fieldtype':'Data','align':'center','width':70})
	columns.append({'fieldname':'cost','label':"Cost",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'sub_total','label':"Sub Total",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'discount','label':"Discount",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'grand_total','label':"Amount",'fieldtype':'Currency','align':'right','width':100})
	columns.append({'fieldname':'profit','label':"Profit",'fieldtype':'Currency','align':'right','width':100})
	return columns

def get_report_data(filters):
	sql = """
		SELECT
			a.parent,
			b.posting_date,
			b.customer,
			sum(a.qty) qty,
			SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
			sum(a.amount) sub_total,
			sum(a.amount) - SUM(a.net_amount) discount,
			SUM(a.net_amount) grand_total,
			SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
		FROM `tabSales Invoice Item` a
		INNER JOIN `tabSales Invoice` b ON b.name = a.parent
		WHERE {0}
		GROUP BY a.parent,b.posting_date,b.customer
	""".format(get_filters(filters))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_report_data1(filters):
	parent_sql = """
		SELECT
			b.customer,
			sum(a.qty) qty,
			SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
			sum(a.amount) sub_total,
			sum(a.amount) - SUM(a.net_amount) discount,
			SUM(a.net_amount) grand_total,
			SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
		FROM `tabSales Invoice Item` a
		INNER JOIN `tabSales Invoice` b ON b.name = a.parent
		WHERE {0}
		GROUP BY b.customer
	""".format(get_filters(filters))
	data=[]
	parent = frappe.db.sql(parent_sql,as_dict=1)
	for dic_p in parent:
		dic_p["indent"] = 0
		dic_p["is_group"]=1
		data.append(dic_p)
		child = frappe.db.sql("""
								SELECT
									a.parent,
									b.posting_date,
									b.customer_name,
									b.customer,
									sum(a.qty) qty,
									SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
									sum(a.amount) sub_total,
									sum(a.amount) - SUM(a.net_amount) discount,
									SUM(a.net_amount) grand_total,
									SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
								FROM `tabSales Invoice Item` a
								INNER JOIN `tabSales Invoice` b ON b.name = a.parent
								WHERE {0} and b.customer = '{1}'
								GROUP BY a.parent,b.posting_date,b.customer_name,b.customer
							""".format(get_filters(filters),dic_p["customer"]), as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"]=0
			data.append(dic_c)
	return data


def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data