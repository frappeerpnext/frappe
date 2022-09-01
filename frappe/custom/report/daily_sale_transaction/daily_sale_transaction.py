# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
def execute(filters=None):
	return get_columns(filters), get_report_data(filters)

def get_columns(filters):
	columns = []

	columns.append({'fieldname':'parent','label':"Document #",'fieldtype':'Data','align':'left','width':200})
	columns.append({'fieldname':'posting_date','label':"Date",'fieldtype':'Data','align':'left','width':100})
	columns.append({'fieldname':'customer','label':"Customer",'fieldtype':'Data','align':'left','width':100})
	columns.append({'fieldname':'qty','label':"QTY",'fieldtype':'Data','align':'left','width':70})
	columns.append({'fieldname':'cost','label':"Cost",'fieldtype':'Currency','align':'left','width':100})
	columns.append({'fieldname':'sub_total','label':"Sub Total",'fieldtype':'Currency','align':'left','width':100})
	columns.append({'fieldname':'discount','label':"Discount",'fieldtype':'Currency','align':'left','width':100})
	columns.append({'fieldname':'grand_total','label':"Amount",'fieldtype':'Currency','align':'left','width':100})
	columns.append({'fieldname':'profit','label':"Profit",'fieldtype':'Currency','align':'left','width':100})
	return columns
def get_report_data(filters):
	con = "b.posting_date BETWEEN '{0}' AND '{1}' AND b.company = '{2}' and a.docstatus=1 and b.docstatus=1".format(filters.start_date,filters.end_date,filters.company)
	if filters.get("price_list"): con = con +	"and b.selling_price_List in ({})".format(filters.price_list)
	if filters.get("customer"):con = con +	"and b.customer in %(customer)s"
	
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
	""".format(con)
	frappe.msgprint("<pre>{}</pre>".format(sql))
	data = frappe.db.sql(sql,as_dict=1)
	return data