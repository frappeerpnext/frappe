# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import data
def execute(filters=None):
	get_data=[]
	get_column=[]
	if filters.group_by == 'Customer' : get_data = get_report_data_group_by_customer(filters);get_column=get_columns_by_customer(filters)
	if filters.group_by == 'Document #' : get_data = get_report_data(filters);get_column=get_columns(filters)
	return get_column, get_data,[],[],get_summary(filters) ,True

def get_filters(filters):
	con = "b.posting_date BETWEEN '{0}' AND '{1}' AND b.company = '{2}' and a.docstatus=1 and b.docstatus=1".format(filters.start_date,filters.end_date,filters.company)
	if filters.get("price_list"): con = con + " and b.selling_price_List in (" + get_list(filters,"price_list") + ")"
	if filters.get("customer"):con = con +	" and b.customer in (" + get_list(filters,"customer") + ")"
	return con

def get_summary(filters):
	sql = """
		SELECT
			count(distinct(b.customer)) customer,
			count(DISTINCT(a.parent)) parent,
			sum(a.qty) qty,
			SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
			sum(a.amount) sub_total,
			sum(a.amount) - SUM(a.net_amount) discount,
			SUM(a.net_amount) grand_total,
			SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit,
			SUM(b.paid_amount) paid_amount,
			sum(a.net_amount-b.paid_amount) balance
		FROM `tabSales Invoice Item` a
		INNER JOIN `tabSales Invoice` b ON b.name = a.parent
		WHERE {0}
	""".format(get_filters(filters))
	data=[]
	sq = frappe.db.sql(sql,as_dict=1)
	data.append({"label":"Customer","value":"{:,.0f}".format(sq[0]["customer"])})
	data.append({"label":"Invoice","value":"{:,.0f}".format(sq[0]["parent"])})
	data.append({"label":"Total QTY","value":"{:,.0f}".format(sq[0]["qty"])})
	data.append({"label":"Total Cost","value":"$ {:,.4f}".format(sq[0]["cost"])})
	data.append({"label":"Sub Total","value":"$ {:,.4f}".format(sq[0]["sub_total"])})
	data.append({"label":"Total Disc.","value":"$ {:,.4f}".format(sq[0]["discount"])})
	data.append({"label":"Grand Total","value":"$ {:,.4f}".format(sq[0]["grand_total"])})
	data.append({"label":"Total Profit","value":"$ {:,.4f}".format(sq[0]["profit"])})
	data.append({"label":"Total Payment","value":"$ {:,.4f}".format(sq[0]["paid_amount"])})
	data.append({"label":"Total Balance","value":"$ {:,.4f}".format(sq[0]["balance"])})
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'parent','label':"Document #",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'posting_date','label':"Date",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'customer_name','label':"Customer",'fieldtype':'Data','align':'left','width':150})
	columns.append({'fieldname':'qty','label':"QTY",'fieldtype':'Data','align':'center','width':70})
	columns.append({'fieldname':'cost','label':"Cost",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'sub_total','label':"Sub Total",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'discount','label':"Discount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'grand_total','label':"Amount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'profit','label':"Profit",'fieldtype':'Currency','align':'right','width':150})
	return columns

def get_columns_by_customer(filters):
	columns = []
	columns.append({'fieldname':'customer_name','label':"Customer",'fieldtype':'Data','align':'center','width':250})
	columns.append({'fieldname':'parent','label':"Document #",'fieldtype':'Data','align':'center','width':200})
	columns.append({'fieldname':'posting_date','label':"Date",'fieldtype':'Data','align':'center','width':100})
	columns.append({'fieldname':'qty','label':"QTY",'fieldtype':'Data','align':'center','width':70})
	columns.append({'fieldname':'cost','label':"Cost",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'sub_total','label':"Sub Total",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'discount','label':"Discount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'grand_total','label':"Amount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'profit','label':"Profit",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'paid_amount','label':"Payment",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'balance','label':"Balance",'fieldtype':'Currency','align':'right','width':150})
	return columns

def get_report_data(filters):
	sql = """
		SELECT
			a.parent,
			b.posting_date,
			b.customer,
			b.customer_name,
			sum(a.qty) qty,
			SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
			sum(a.amount) sub_total,
			sum(a.amount) - SUM(a.net_amount) discount,
			SUM(a.net_amount) grand_total,
			SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
		FROM `tabSales Invoice Item` a
		INNER JOIN `tabSales Invoice` b ON b.name = a.parent
		WHERE {0}
		GROUP BY a.parent,b.posting_date,b.customer,b.customer_name
	""".format(get_filters(filters))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_report_data_group_by_customer(filters):
	parent_sql = """
		SELECT
			b.customer,
			CONCAT(b.customer_name," / ",coalesce(c.phone_number,"")) as customer_name,
			count(DISTINCT(a.parent)) parent,
			sum(a.qty) qty,
			SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
			sum(a.amount) sub_total,
			sum(a.amount) - SUM(a.net_amount) discount,
			SUM(a.net_amount) grand_total,
			SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit,
			SUM(b.paid_amount) paid_amount,
			sum(a.net_amount-b.paid_amount) balance
		FROM `tabSales Invoice Item` a
		INNER JOIN `tabSales Invoice` b ON b.name = a.parent
		INNER JOIN `tabCustomer` c ON c.name = b.customer
		WHERE {0}
		GROUP BY b.customer,b.customer_name,c.phone_number
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
									sum(a.qty) qty,
									SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
									sum(a.amount) sub_total,
									sum(a.amount) - SUM(a.net_amount) discount,
									SUM(a.net_amount) grand_total,
									SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit,
									SUM(paid_amount) paid_amount,
									sum(a.net_amount-b.paid_amount) balance
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