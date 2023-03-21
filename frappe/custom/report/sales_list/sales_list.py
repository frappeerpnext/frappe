# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	columns = []
	columns.append({'fieldname':'pos_profile','label':"Item Group Type",'fieldtype':'Data','align':'left','width':200})
	columns.append({'label':'Gross Sales','fieldname':"amount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'Excluded VAT','fieldname':"exclude_vat",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'Excluded PLT','fieldname':"exclude_plt",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'PLT 3%','fieldname':"plt",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'VAT 10%','fieldname':"vat",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'Discount','fieldname':"discount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'FOC','fieldname':"foc_amount",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'Net Sales','fieldname':"net",'fieldtype':'Currency','align':'right','width':150})
	columns.append({'label':'Remark','fieldname':"Amount",'fieldtype':'Currency','align':'right','width':150})
	return columns

def get_data(filters):
	data=[]
	parent_data=[]
	parent = """
				SELECT 
					'Ticket' pos_profile,
					SUM(coalesce(a.net_amount,0)) amount,
					SUM(coalesce(a.net_amount,0))/1.1 exclude_vat,
					SUM(coalesce(a.net_amount,0))/1.1/1.006 exclude_plt,
					SUM(coalesce(a.net_amount,0))/1.1/1.006*0.006 plt,
					SUM(coalesce(a.net_amount,0))/1.1 * 0.1 vat,
					SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) discount,
					Sum(coalesce(if(a.is_foc=1, (if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount,0))) foc_amount,
					SUM(coalesce(a.net_amount,0))-SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) net
				FROM `tabSales Invoice Item` a
					INNER JOIN `tabItem Group` b ON b.name = a.item_group
					INNER JOIN `tabSales Invoice` c ON c.name = a.parent
				WHERE c.posting_date = '{0}' and c.docstatus = 1 and coalesce(c.department,'') <> 'Souvenir - AWA' and  (coalesce(c.department,'')='Sales & Marketing - AWA' or coalesce(a.is_ticket,0)=1)
			""".format(filters.date)
	ticket_data = frappe.db.sql(parent,as_dict=1)
	if ticket_data[0].pos_profile == "Ticket" and  ticket_data[0].amount:
		parent_data = ticket_data
	for dic_p in parent_data:
		dic_p["indent"] = 0
		dic_p["is_group"] = 1
		data.append(dic_p)
		child_data = ("""
						SELECT 
							if(coalesce(c.department,'')='Ticketing - AWA',concat(count(distinct c.pos_profile),' POSs'),coalesce(c.department,'')) pos_profile,
							SUM(coalesce(a.net_amount,0)) amount,
							SUM(coalesce(a.net_amount,0))/1.1 exclude_vat,
							SUM(coalesce(a.net_amount,0))/1.1/1.006 exclude_plt,
							SUM(coalesce(a.net_amount,0))/1.1/1.006*0.006 plt,
							SUM(coalesce(a.net_amount,0))/1.1 * 0.1 vat,
							SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) discount,
       						Sum(coalesce(if(a.is_foc=1, (if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount,0))) foc_amount,
							SUM(coalesce(a.net_amount,0))-SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) net
						FROM `tabSales Invoice Item` a
							INNER JOIN `tabItem Group` b ON b.name = a.item_group
							INNER JOIN `tabSales Invoice` c ON c.name = a.parent
						WHERE c.posting_date = '{0}' and c.docstatus = 1 and coalesce(c.department,'') <> 'Souvenir - AWA' and (coalesce(c.department,'')='Sales & Marketing - AWA' or coalesce(a.is_ticket,0)=1)
							group by coalesce(c.department,'')
					""".format(filters.date))
		child = frappe.db.sql(child_data,as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)
	parent = """
				SELECT 
					coalesce(c.pos_profile,'Not Set') pos_profile,
					SUM(coalesce(a.net_amount,0)) amount,
					SUM(coalesce(a.net_amount,0))/1.1 exclude_vat,
					SUM(coalesce(a.net_amount,0))/1.1/1.006 exclude_plt,
					SUM(coalesce(a.net_amount,0))/1.1/1.006*0.006 plt,
					SUM(coalesce(a.net_amount,0))/1.1 * 0.1 vat,
					SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) discount,
					Sum(coalesce(if(a.is_foc=1, (if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount,0))) foc_amount,
     				SUM(coalesce(a.net_amount,0))-SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) net
				FROM `tabSales Invoice Item` a
					INNER JOIN `tabItem Group` b ON b.name = a.item_group
					INNER JOIN `tabSales Invoice` c ON c.name = a.parent
				WHERE c.posting_date = '{0}' and c.docstatus = 1 and coalesce(c.department,'') not in ('Sales & Marketing - AWA','Souvenir - AWA') and coalesce(a.is_ticket,0)=0
					GROUP BY coalesce(c.pos_profile,'Not Set')
			""".format(filters.date)
	parent_data = frappe.db.sql(parent,as_dict=1)
	for dic_p in parent_data:
		dic_p["indent"] = 0
		dic_p["is_group"] = 1
		data.append(dic_p)
		child_data = ("""
						SELECT 
							coalesce(b.item_group_type,'Not Set') pos_profile,
							SUM(coalesce(a.net_amount,0)) amount,
							SUM(coalesce(a.net_amount,0))/1.1 exclude_vat,
							SUM(coalesce(a.net_amount,0))/1.1/1.006 exclude_plt,
							SUM(coalesce(a.net_amount,0))/1.1/1.006*0.006 plt,
							SUM(coalesce(a.net_amount,0))/1.1 * 0.1 vat,
							SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) discount,
							Sum(coalesce(if(a.is_foc=1, (if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount,0))) foc_amount,
       						SUM(coalesce(a.net_amount,0))-SUM(coalesce(if(a.is_foc,0,(if(c.posting_date<'2022-12-20',a.base_rate,a.base_price_list_rate))*a.qty-a.net_amount),0)) net
						FROM `tabSales Invoice Item` a
							INNER JOIN `tabItem Group` b ON b.name = a.item_group
							INNER JOIN `tabSales Invoice` c ON c.name = a.parent
						WHERE c.posting_date = '{0}' and c.docstatus = 1 AND c.pos_profile = '{1}'
							GROUP BY b.item_group_type
					""".format(filters.date,dic_p["pos_profile"]))
		child = frappe.db.sql(child_data,as_dict=1)
		for dic_c in child:
			dic_c["indent"] = 1
			dic_c["is_group"] = 0
			data.append(dic_c)
	if data:
		data.append({"pos_profile":"Totals",
		"amount": sum(c.amount for c in data if c.is_group == 1),
		"exclude_vat": sum(c.exclude_vat for c in data if c.is_group == 1),
		"exclude_plt": sum(c.exclude_plt for c in data if c.is_group == 1),
		"plt": sum(c.plt for c in data if c.is_group == 1),
		"vat": sum(c.vat for c in data if c.is_group == 1),
		"discount": sum(c.discount for c in data if c.is_group == 1),
		"foc_amount": sum(c.foc_amount for c in data if c.is_group == 1),
		"net": sum(c.net for c in data if c.is_group == 1),
		"is_group": 1})
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x.replace("'", "''")) for x in filters.get(name))
	return data