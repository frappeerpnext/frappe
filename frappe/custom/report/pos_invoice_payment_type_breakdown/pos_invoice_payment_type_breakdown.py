# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	return get_columns(filters),get_report_data(filters)


def get_columns(filters):
	columns = []
	columns.append({'fieldname':'mode_of_payment','label':"Payment Type",'fieldtype':'Data','align':'center','width':150})
	columns.append({'fieldname':'payment_amount','label':"Payment Amount",'fieldtype':'Currency','align':'right','width':150})
	return columns

def get_report_data(filters):
	check_amount = """SELECT 
						count(a.mode_of_payment) as mode_of_payment,
						SUM(if(a.mode_of_payment='Cash',1,0)) AS cash
						FROM 
							`tabSales Invoice Payment` a 
							inner join `tabSales Invoice` b on b.name = a.parent 
						WHERE
							b.posting_date between '{0}' and '{1}' and 
							b.company = '{2}' and b.docstatus = 1 and b.branch = case when '{3}' = 'None' then b.branch else '{3}' end
						GROUP BY a.parent""".format(filters.start_date,filters.end_date,filters.company,filters.branch)
	ch_data = frappe.db.sql(check_amount,as_dict=1)
	union=""
	if(len(ch_data)>0) : 
		if(ch_data[0]["mode_of_payment"] > 0 and ch_data[0]["cash"] == 0 )  : union = """UNION ALL SELECT 'Cash' mode_of_payment,0 payment_amount"""
	sql = """
				WITH change_amount AS (
					SELECT 
					'Cash' AS mode_of_payment, 
					SUM(change_amount) AS change_amount
				FROM `tabSales Invoice`  
				where
				docstatus = 1 AND 
				posting_date between '{0}' and '{1}' and 
				company = '{2}' and branch = case when '{4}' = 'None' then branch else '{4}' end
				),paid_amount AS (
					SELECT 
						a.mode_of_payment, 
					SUM(a.amount) AS `payment_amount` 
					FROM 
						`tabSales Invoice Payment` a 
						inner join `tabSales Invoice` b on b.name = a.parent 
					WHERE
						b.posting_date between '{0}' and '{1}' and 
						b.company = '{2}' and 
						b.docstatus = 1 and b.branch = case when '{4}' = 'None' then b.branch else '{4}' end
					GROUP BY mode_of_payment
				)
				SELECT 
				a.mode_of_payment, 
				a.payment_amount - IFNULL(b.change_amount,0) AS `payment_amount` 
				FROM( select
				a.mode_of_payment, 
				a.payment_amount 
				FROM  paid_amount a
				{3}
				)a 
				left JOIN change_amount b ON b.mode_of_payment = a.mode_of_payment
				""".format(filters.start_date,filters.end_date,filters.company,union,filters.branch)
	data = frappe.db.sql(sql,as_dict=1)
	return data
