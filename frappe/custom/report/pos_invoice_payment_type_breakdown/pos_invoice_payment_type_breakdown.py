# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = [], []
	return get_columns(filters),get_report_data(filters)


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

def get_report_data(filters):
	sql = """
DELIMITER $
BEGIN NOT ATOMIC
if(
SELECT count(a.mode_of_payment) id 
FROM `tabSales Invoice Payment` a 
inner join `tabSales Invoice` b on b.name = a.parent 
WHERE b.posting_date between '{0}' and '{1}' and b.company = '{2}' and b.docstatus = 1)=0
Then
WITH change_amount AS ( 
SELECT 'Cash' AS mode_of_payment, 
SUM(change_amount) AS change_amount 
FROM `tabPOS Invoice` where docstatus = 1 AND posting_date between '{0}' and '{1}' and company = '{2}' )
,paid_amount AS ( 
SELECT a.mode_of_payment, 
SUM(a.amount) AS `payment_amount` 
FROM `tabSales Invoice Payment` a 
inner join `tabPOS Invoice` b on b.name = a.parent 
WHERE b.posting_date between '{0}' and '{1}' and b.company = '{2}' and b.docstatus = 1 GROUP BY mode_of_payment ) 
SELECT 
a.mode_of_payment, 
a.payment_amount - IFNULL(b.change_amount,0) AS `payment_amount` 
FROM ( SELECT a.mode_of_payment, a.payment_amount FROM paid_amount a 
UNION ALL SELECT 'Cash' AS mode_of_payment,0 AS payment_amount) a 
left JOIN change_amount b ON b.mode_of_payment = a.mode_of_payment; 
ELSE
WITH change_amount AS ( 
SELECT 'Cash' AS mode_of_payment, 
SUM(change_amount) AS change_amount 
FROM `tabPOS Invoice` where docstatus = 1 AND posting_date between '{0}' and '{1}' and company = '{2}' )
,paid_amount AS ( 
SELECT a.mode_of_payment,
 SUM(a.amount) AS `payment_amount` 
 FROM `tabSales Invoice Payment` a 
 inner join `tabPOS Invoice` b on b.name = a.parent WHERE b.posting_date between '{0}' and '{1}' and b.company = '{2}' and b.docstatus = 1 
 GROUP BY mode_of_payment ) 
 SELECT a.mode_of_payment, a.payment_amount - IFNULL(b.change_amount,0) AS `payment_amount` 
 FROM paid_amount a left JOIN change_amount b ON b.mode_of_payment = a.mode_of_payment; 
 END if; 
 end $ 
 DELIMITER ;
	""".format(filters.start_date,filters.end_date,filters.company)
	frappe.msgprint(sql)
	data = frappe.db.sql(sql,as_dict=1)
	return data
