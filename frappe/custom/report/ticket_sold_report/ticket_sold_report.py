# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import strip

def execute(filters=None):
	return get_columns(filters), get_data(filters),get_fields(filters)

def get_filters(filters):
	data= " and transaction_date between '{}' AND '{}'".format(filters.start_date,filters.end_date)
	return data
def get_row_group(filters):
	data = ""
	data = get_row_groups(filters.row_group)
	return data

def get_columns(filters):
	columns = []
	columns.append({'fieldname':"{}".format(get_row_groups(filters.row_group)),'label':"{}".format(filters.row_group),'fieldtype':'Data','align':'left','width':200,'height':100})
	fields = get_fields(filters)
	for f in fields:
			columns.append({
					'fieldname':"total_" +  f['fieldname'],
					'label':"Total " + f["label"],
					}
				)
	return columns

def get_data(filters):
	sql = ""
	data=[]
	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			sql = strip(sql)
			sql = sql + """
						SELECT 
							SUM(price) amount
						FROM `tabPOS Ticket` 
							WHERE pos_invoice_id IS NOT NULL and transaction_date between {0} and {1}
						group by {2};
					""".format(f["start_date"],f["end_date"],get_row_group(filters))
	frappe.msgprint(sql)
	data = frappe.db.sql(sql,as_dict=1)
	return data

def get_list(filters,name):
	data = ','.join("'{0}'".format(x) for x in filters.get(name))
	return data

def get_row_groups(row_group):
	data= ""
	if(row_group) == "Item": data = "item_name"
	if(row_group) == "Sale Invoice": data = "pos_invoice"
	if(row_group) == "Date": data = "transaction_date"
	if(row_group) == "Cashier": data = "pos_username"
	return data

def get_fields(filters):
	sql=""
	if filters.column_group=="Daily":
		sql = """
			select 
				concat('col_',date_format(date,'%d_%m')) as fieldname, 
				date_format(date,'%d') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%d_%m')) , 
				date_format(date,'%d')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group =="Monthly":
		sql = """
			select 
				concat('col_',date_format(date,'%m_%Y')) as fieldname, 
				date_format(date,'%b %y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%m_%Y')) , 
				date_format(date,'%b %y')  	
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Yearly":
		sql = """
			select 
				concat('col_',date_format(date,'%Y')) as fieldname, 
				date_format(date,'%Y') as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%Y')),
				date_format(date,'%Y')
		""".format(filters.start_date, filters.end_date)
	fields = frappe.db.sql(sql,as_dict=1)
	return fields