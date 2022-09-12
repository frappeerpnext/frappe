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
	con = "b.posting_date BETWEEN '{0}' AND '{1}' AND b.company = '{2}' and b.docstatus=1".format(filters.start_date,filters.end_date,filters.company)
	if filters.get("price_list"): con = con + " and b.selling_price_List in (" + get_list(filters,"price_list") + ")"
	if filters.get("customer"):con = con +	" and b.customer in (" + get_list(filters,"customer") + ")"
	return con

def get_summary(filters):
	sql = """
		WITH sale_data AS(SELECT 
			a.parent name,
			count(distinct(b.customer)) customer,
			count(DISTINCT(a.parent)) parent,
			sum(a.qty) qty,
			SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
			sum(a.amount) sub_total,
			sum(a.amount) - SUM(a.net_amount) discount,
			SUM(a.net_amount) grand_total,
			SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
		FROM `tabSales Invoice Item` a 
			INNER JOIN `tabSales Invoice` b ON b.name = a.parent 
			INNER JOIN `tabCustomer` c ON c.name = b.customer 
		WHERE {0}
			GROUP BY a.parent)
			,paid_amount AS(
			SELECT 
				name,
				paid_amount
			FROM `tabSales Invoice` b
			WHERE {0} 
			GROUP BY name)
			SELECT 
				count(customer) customer,
				count(parent) parent,
				sum(qty) qty,
				sum(cost) cost,
				sum(sub_total) sub_total,
				sum(discount) discount,
				sum(grand_total) grand_total,
				sum(profit) profit,
				sum(b.paid_amount) paid_amount,
				sum(a.grand_total - b.paid_amount) balance
			FROM sale_data a
			INNER JOIN paid_amount b ON b.name = a.name
	""".format(get_filters(filters))
	data=[]
	sq = frappe.db.sql(sql,as_dict=1)
	if sq[0]["customer"] != 0:
		data.append({"label":"Total Cost","value":"$ {:,.4f}".format(sq[0]["cost"])})
		data.append({"label":"Grand Total","value":"$ {:,.4f}".format(sq[0]["grand_total"])})
		data.append({"label":"Total Profit","value":"$ {:,.4f}".format(sq[0]["profit"])})
		data.append({"label":"Total Payment","value":"$ {:,.4f}".format(sq[0]["paid_amount"])})
		data.append({"label":"Total Balance","value":"$ {:,.4f}".format(sq[0]["balance"])})
	else:
		data = None
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
	columns.append({'fieldname':'paid_amount','label':"Payment",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'fieldname':'balance','label':"Balance",'fieldtype':'Currency','align':'right','width':150})
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
		WITH sale_data AS(
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
		GROUP BY a.parent,b.posting_date,b.customer,b.customer_name)
		,paid_amount AS(
		SELECT 
			name,
			paid_amount
		FROM `tabSales Invoice` b
		WHERE {0}
		and docstatus=1 GROUP BY name)
		SELECT 
			a.*,
			b.paid_amount,
			a.grand_total - b.paid_amount balance
		FROM sale_data a
		INNER JOIN paid_amount b ON b.name = a.parent
	""".format(get_filters(filters))
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_report_data_group_by_customer(filters):
	parent_sql = """
			WITH sale_data AS(
				SELECT 
					b.customer, 
					CONCAT(b.customer_name," / ",coalesce(c.phone_number,"")) as customer_name, 
					count(DISTINCT(a.parent)) parent, 
					sum(a.qty) qty, 
					SUM(COALESCE(a.incoming_rate,0)*a.qty) cost, 
					sum(a.amount) sub_total, sum(a.amount) - SUM(a.net_amount) discount, 
					SUM(a.net_amount) grand_total, 
					SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
				FROM `tabSales Invoice Item` a 
				INNER JOIN `tabSales Invoice` b ON b.name = a.parent 
				INNER JOIN `tabCustomer` c ON c.name = b.customer 
				WHERE {0}
			GROUP BY b.customer,b.customer_name,c.phone_number)
				,paid_amount AS(
				SELECT 
					customer,
					paid_amount
				FROM `tabSales Invoice` b
				WHERE {0}
				GROUP BY customer)
				SELECT 
					a.*,
					b.paid_amount,
					a.grand_total - b.paid_amount balance
				FROM sale_data a
				INNER JOIN paid_amount b ON b.customer = a.customer
	""".format(get_filters(filters))
	data=[]
	parent = frappe.db.sql(parent_sql,as_dict=1)
	for dic_p in parent:
		dic_p["indent"] = 0
		dic_p["is_group"]=1
		data.append(dic_p)
		child = frappe.db.sql("""
								WITH sale_data AS(SELECT
									a.parent,
									b.posting_date,
									sum(a.qty) qty,
									SUM(COALESCE(a.incoming_rate,0)*a.qty) cost,
									sum(a.amount) sub_total,
									sum(a.amount) - SUM(a.net_amount) discount,
									SUM(a.net_amount) grand_total,
									SUM(a.net_amount) - SUM(coalesce(a.incoming_rate,0)*a.qty) profit
								FROM `tabSales Invoice Item` a
								INNER JOIN `tabSales Invoice` b ON b.name = a.parent
								WHERE {0} and b.customer = '{1}'
								GROUP BY a.parent,b.posting_date,b.customer_name,b.customer)
								,paid_amount AS(
								SELECT 
									name,
									paid_amount
								FROM `tabSales Invoice` b
								WHERE {0} and b.customer = '{1}'
								and docstatus=1 GROUP BY name)
								SELECT 
									a.*,
									b.paid_amount,
									a.grand_total - b.paid_amount balance
								FROM sale_data a
								INNER JOIN paid_amount b ON b.name = a.parent
							""".format(get_filters(filters),dic_p["customer"]), as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"]=0
			data.append(dic_c)
	return data


def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data