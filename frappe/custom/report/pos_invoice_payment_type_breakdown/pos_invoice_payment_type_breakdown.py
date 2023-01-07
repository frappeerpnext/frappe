# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	return get_columns(filters),get_report_data(filters)


def get_columns(filters):
	columns = []
	columns.append({'fieldname':'mode_of_payment','label':"Payment Type",'fieldtype':'Data','align':'center','width':150})
	columns.append({'fieldname':'payment_amount','label':"Payment Amount",'fieldtype':'Currency','align':'right','width':150})
	# columns.append({'fieldname':'closing_amount','label':"Actual Amount",'fieldtype':'Currency','align':'right','width':150})
	# columns.append({'fieldname':'different_amount','label':"Different",'fieldtype':'Currency','align':'right','width':150})
	return columns

def get_report_data(filters):
	branch = ""
	if filters.branch : branch = " and b.branch in (" + get_list(filters,"branch") + ")"
	check_amount = """SELECT 
						1 has_cash
						FROM 
							`tabSales Invoice Payment` a 
							inner join `tabSales Invoice` b on b.name = a.parent 
						WHERE
							b.posting_date between '{0}' and '{1}' and a.mode_of_payment='Cash' and
							b.company = '{2}' and b.docstatus = 1 {3}
						GROUP BY a.mode_of_payment""".format(filters.start_date,filters.end_date,filters.company,branch)
	ch_data = frappe.db.sql(check_amount,as_dict=1)
	union=""
	if(len(ch_data)<=0) : union = """UNION ALL SELECT 'Cash' mode_of_payment,0 payment_amount"""
	sql = """
				WITH change_amount AS (
					SELECT 
					'Cash' AS mode_of_payment, 
					SUM(change_amount) AS change_amount
				FROM `tabPOS Invoice`  b
				where
				b.docstatus = 1 AND 
				b.posting_date between '{0}' and '{1}' and 
				company = '{2}' {4}
				),paid_amount AS (
					SELECT 
						a.mode_of_payment, 
					SUM(a.amount+write_off_amount) AS `payment_amount` 
					FROM 
						`tabSales Invoice Payment` a 
						inner join `tabPOS Invoice` b on b.name = a.parent 
					WHERE
						b.posting_date between '{0}' and '{1}' and 
						b.company = '{2}' and 
						b.docstatus = 1 {4}
					GROUP BY mode_of_payment
				), opening_id as(SELECT 
					pos_opening_entry_id
					FROM `tabPOS Invoice` b
					where
						b.docstatus = 1 AND 
						b.posting_date between '{0}' and '{1}' and 
						b.company = '{2}' {4}
					group by 
						pos_opening_entry_id)
					,closing_amount AS(
					SELECT 
						b.mode_of_payment,
						SUM(b.closing_amount-b.opening_amount) closing_amount
					FROM  `tabPOS Closing Entry` a
					INNER JOIN `tabPOS Closing Entry Detail` b ON b.parent = a.name
					WHERE a.pos_opening_entry_id IN(SELECT * FROM opening_id)
					GROUP BY 
						b.mode_of_payment)
				,total_amount AS(
					select
					sum(a.payment_amount - coalesce(change_amount,0)) amount
					FROM paid_amount a
					left JOIN change_amount b ON b.mode_of_payment = a.mode_of_payment
					WHERE a.mode_of_payment IN ('Cash','Cash KHR'))
				,cash_percent AS(	
					select
					a.mode_of_payment,
					if(a.mode_of_payment = 'Cash' OR a.mode_of_payment = 'Cash KHR',((a.payment_amount - coalesce(change_amount,0))/c.amount),1) percent
					FROM paid_amount a
					left JOIN change_amount b ON b.mode_of_payment = a.mode_of_payment
					LEFT JOIN total_amount c ON 1=1)
				SELECT 
				a.mode_of_payment, 
				a.payment_amount - IFNULL(b.change_amount,0) AS 'payment_amount',
				(if(a.mode_of_payment = 'Cash KHR',(select closing_amount FROM closing_amount WHERE mode_of_payment = 'Cash'),c.closing_amount) * d.percent) closing_amount,
				(if(a.mode_of_payment = 'Cash KHR',(select coalesce(closing_amount,0) FROM closing_amount WHERE mode_of_payment = 'Cash'),coalesce(c.closing_amount,0)) * coalesce(d.percent,0)) + coalesce(b.change_amount,0) - coalesce(a.payment_amount,0) different_amount
				FROM( select
				a.mode_of_payment, 
				a.payment_amount 
				FROM  paid_amount a
				{3}
				)a 
				left JOIN change_amount b ON b.mode_of_payment = a.mode_of_payment
				left join closing_amount c on c.mode_of_payment = a.mode_of_payment
				LEFT JOIN cash_percent d ON d.mode_of_payment = a.mode_of_payment
				""".format(filters.start_date,filters.end_date,filters.company,union,branch)
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data