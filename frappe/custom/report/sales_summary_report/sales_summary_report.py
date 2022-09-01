# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

from dataclasses import field
from email.errors import MessageParseError
from fnmatch import filter
from importlib.metadata import files
import frappe
from frappe.utils import date_diff
import json

def execute(filters=None):
 
	validate(filters)
	#run this to update parent_item_group in table sales invoice item
	update_parent_item_group()
	update_sale()
	report_data = get_report_data(filters)

	report_chart = None
	if filters.chart_type !="None" and len(report_data)<=100:
		report_chart = get_report_chart(filters,report_data)

 
	return get_columns(filters), report_data, None, report_chart, get_report_summary(report_data,filters)




def validate(filters):

	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:

			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))

	
	if filters.column_group=="Daily":
		n = date_diff(filters.end_date, filters.start_date)
		if n>30:
			frappe.throw("Date range cannot greater than 30 days")

def update_parent_item_group():
	frappe.db.sql(
		"""
			UPDATE `tabSales Invoice Item` a 
			SET parent_item_group = (
					SELECT parent_item_group FROM `tabItem Group` WHERE NAME=a.item_group) 
			WHERE ifnull(parent_item_group,'') = ''
		"""
	)

def update_sale():
	frappe.db.sql(
		"""
			UPDATE `tabSales Invoice Item` a 
			SET parent_item_group = (
					SELECT parent_item_group FROM `tabItem Group` WHERE NAME=a.item_group) 
			WHERE ifnull(parent_item_group,'') = ''
		"""
	)

	#update transaction to tbl sale invoice item
	sale_invoices = frappe.db.sql("select distinct parent from `tabSales Invoice Item` where total_transaction=0", as_dict=1)
	
	if sale_invoices:
		for s in sale_invoices:
			 
			item_count = frappe.db.sql("select count(name) as total from `tabSales Invoice Item` where parent='{}'".format(s["parent"]), as_dict=1)
			
			if item_count:
				total_item = item_count[0]["total"]
				#get total transaction from pos invoice
				pos_invoice_count = frappe.db.sql("select count(name) as total from `tabPOS Invoice` where consolidated_invoice='{}'".format(s["parent"]), as_dict=1)
				total_pos_invoice = 1
				if pos_invoice_count and pos_invoice_count[0]["total"]>1:
						total_pos_invoice = pos_invoice_count[0]["total"]

				sql = "update `tabSales Invoice Item` set total_transaction = {} where parent='{}'".format(total_pos_invoice/total_item, s["parent"])
				 
				frappe.db.sql(sql)
	
	frappe.db.commit()
	#end update total transaction to sale invoice item
	# 				

def get_columns(filters):
	
	columns = []

	columns.append({'fieldname':'row_group','label':filters.row_group,'fieldtype':'Data','align':'left','width':250})

	hide_columns = filters.get("hide_columns")
	 
	if filters.column_group !="None" and filters.row_group not in ["Date","Month","Year"]:
		 
		for c in get_dynamic_columns(filters):
			columns.append(c)

	#add total to last column
	if not hide_columns or  "Transaction" not in hide_columns:
		columns.append({
				'fieldname':'total_transaction',
				'label':"Total Tran.",
				'fieldtype':'Float',
				'precision': 2,
				'align':'center'}
			)
	if not hide_columns or  "Quantity" not in hide_columns:
		columns.append({
				'fieldname':'total_qty',
				'label':"Total Qty",
				'fieldtype':'Float',
				'precision': 2,
				'align':'center'}
			)

	if not hide_columns or  "Sub Total" not in hide_columns:
		columns.append({
				'fieldname':'sub_total',
				'label':"Sub Total",
				'fieldtype':'Currency',
				'align':'right'
				}
			)

	if not hide_columns or  "Cost" not in hide_columns:
		columns.append({
				'fieldname':'total_cost',
				'label':"Total Cost",
				'fieldtype':'Currency',
				'align':'right'}
			)


	columns.append({
		'fieldname':'total_amount',
		'label':"Total Amt",
		'fieldtype':'Currency',
		'align':'right'}
	)

	if not hide_columns or  "Profit" not in hide_columns:
		columns.append({
				'fieldname':'total_profit',
				'label':"Total Profit",
				'fieldtype':'Currency',
				'align':'right'}
			)

	return columns



def get_dynamic_columns(filters):
	hide_columns = filters.get("hide_columns")
	fields = get_fields(filters)

	columns=[]
	for f in fields:
		if not hide_columns or  "Transaction" not in hide_columns:
			columns.append({
				'fieldname':f["fieldname"] +"_transaction",
				'label': f["label"] + " Tran.",
				'fieldtype':'Float',
				'precision': 2,
				'align':'center'}
			)

		if not hide_columns or  "Quantity" not in hide_columns:
			columns.append({
				'fieldname':f["fieldname"] +"_qty",
				'label': f["label"] + " Qty",
				'fieldtype':'Float',
				'precision': 2,
				'align':'center'}
			)

		if not hide_columns or  "Sub Total" not in hide_columns:
			columns.append({
				'fieldname':f["fieldname"] +"_sub_total",
				'label': f["label"] + " Sub Total",
				'fieldtype':'Currency',
				'align':'right'}
			)

		if not hide_columns or  "Cost" not in hide_columns:
			columns.append({
				'fieldname':f["fieldname"] +"_cost",
				'label':f["label"] + " Cost",
				'fieldtype':'Currency',
				'align':'center'}
			)


		columns.append({
			'fieldname':f["fieldname"] +"_amt",
			'label':f["label"] + " Amt",
			'fieldtype':'Currency',
			'align':'right'}
		)

		if not hide_columns or  "Profit" not in hide_columns:
			columns.append({
				'fieldname':f["fieldname"] +"_profit",
				'label':f["label"] + " Profit",
				'fieldtype':'Currency',
				'align':'center'}
			)

		
	return columns

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
	elif filters.column_group=="Weekly":
		sql = """
			select 
				concat('col_',date_format(date,'%v_%Y')) as fieldname, 
				concat('WK ',date_format(date,'%v %y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',date_format(date,'%v_%Y')), 
				concat('WK ',date_format(date,'%v %y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Quarterly":
		sql = """
			select 
				concat('col_',QUARTER(date)) as fieldname, 
				concat('Q',QUARTER(date),' ',date_format(date,'%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',QUARTER(date)),
				concat('Q',QUARTER(date),' ',date_format(date,'%y')) 
		""".format(filters.start_date, filters.end_date)
	elif filters.column_group=="Half Yearly":
		sql = """
			select 
				concat('col_',if(month(date) between 1 and 6,'jan_jun','jul_dec'),date_format(date,'%y')) as fieldname, 
				concat(if(month(date) between 1 and 6,'Jan-Jun','Jul-Dec'),' ',date_format(date,'%y')) as label ,
				min(date) as start_date,
				max(date) as end_date
			from `tabDates` 
			where date between '{}' and '{}'
			group by
				concat('col_',if(month(date) between 1 and 6,'jan_jun','jul_dec'),date_format(date,'%y')), 
				concat(if(month(date) between 1 and 6,'Jan-Jun','Jul-Dec'),' ',date_format(date,'%y')) 
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

def get_conditions(filters):

	conditions = ""
	conditions += " b.company =if('{0}'='None',b.company,'{0}')".format(filters.company)
	conditions += " AND b.posting_date between %(start_date)s AND %(end_date)s"
	 
	if filters.get("item_group"):
		conditions += " AND a.parent_item_group in %(item_group)s"

	if filters.get("price_list"):
		conditions += " AND b.selling_price_list in %(price_list)s"
	
 
	return conditions

def get_report_data(filters):
	hide_columns = filters.get("hide_columns")
	row_group = [d["fieldname"] for d in get_row_groups() if d["label"]==filters.row_group][0]
	 
	
	

	sql = "select {} as row_group ".format(row_group)
	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			sql = sql + ','
			if not hide_columns or  "Transaction" not in hide_columns:
				sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',a.total_transaction,0)) as {}_transaction,".format(f["start_date"],f["end_date"],f["fieldname"])
			
			if not hide_columns or  "Quantity" not in hide_columns:
				sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',a.qty,0)) as {}_qty,".format(f["start_date"],f["end_date"],f["fieldname"])
			
			#sub total column dynamic
			if not hide_columns or  "Sub Total" not in hide_columns:
				sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',a.amount,0)) as {}_sub_total,".format(f["start_date"],f["end_date"],f["fieldname"])
			
			# cost columns
			if not hide_columns or  "Cost" not in hide_columns:
				sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',a.qty*a.incoming_rate,0)) as {}_cost,".format(f["start_date"],f["end_date"],f["fieldname"])

			# profit columns
			if not hide_columns or  "Profit" not in hide_columns:
				sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',a.net_amount - (a.qty*a.incoming_rate),0)) as {}_profit,".format(f["start_date"],f["end_date"],f["fieldname"])
			
			

			sql = sql +	"SUM(if(b.posting_date between '{}' AND '{}',a.net_amount,0)) as {}_amt".format(f["start_date"],f["end_date"],f["fieldname"])

			#end for
 
	if not hide_columns or  "Transaction" not in hide_columns:
		sql = sql + ",SUM(a.total_transaction) AS total_transaction "

	if not hide_columns or  "Quantity" not in hide_columns:
		sql = sql + ",SUM(qty) AS total_qty "

	#total sub total
	if not hide_columns or  "Sub Total" not in hide_columns:
		sql = sql + ",SUM(a.amount) AS sub_total "
	
	if not hide_columns or  "Cost" not in hide_columns:
		sql = sql + ",SUM(a.qty*a.incoming_rate) AS total_cost "

	sql = sql + ",SUM(a.net_amount) AS total_amount "

	#chekc if column total profit not hide
	if not hide_columns or  "Profit" not in hide_columns:
		sql = sql + ",SUM(a.net_amount - (  a.qty*a.incoming_rate)) AS total_profit "

	
	sql = sql + """
		FROM `tabSales Invoice Item` AS a
			INNER JOIN `tabSales Invoice` b on b.name = a.parent
		WHERE
			b.docstatus in (1) AND
			{0}
		GROUP BY 
		{1}
	""".format(get_conditions(filters), row_group)
 
	data = frappe.db.sql(sql,filters, as_dict=1)
	return data
 

def get_report_summary(data,filters):
	hide_columns = filters.get("hide_columns")
	total_amount = frappe.utils.fmt_money(sum(d["total_amount"] for d in data))
	 
	report_summary =[{"label":"Total " + filters.row_group ,"value":len(data),'indicator':'Red'}]

	if not hide_columns or  "Transaction" not in hide_columns:
		report_summary.append({"label":"Total Transaction","value":"{:.2f}".format(sum(d["total_transaction"] for d in data))})	
		
	if not hide_columns or  "Quantity" not in hide_columns:
		report_summary.append({"label":"Total Quantity","value":sum(d["total_qty"] for d in data),'indicator':'Green'})	
	
	#sub total
	if not hide_columns or  "Sub Total" not in hide_columns:
		report_summary.append({"label":"Sub Total","value":sum(d["sub_total"] for d in data),'indicator':'blue'})	
	

	if not hide_columns or  "Cost" not in hide_columns:
		report_summary.append({"label":"Total Cost","value":frappe.utils.fmt_money(sum(d["total_cost"] for d in data)),'indicator':'Blue'})


	report_summary.append({"label":"Total Amount","value":total_amount,'indicator':'#2E7D32'})

	if not hide_columns or  "Profit" not in hide_columns:
		report_summary.append({"label":"Total Profit","value":frappe.utils.fmt_money(sum(d["total_profit"] for d in data)),'indicator':'#FF3D00'})

 
	return report_summary

def get_report_chart(filters,data):
	columns = []
	amounts = []
	costs = []
	profits = []
	quantities = []
	transactions = []
	sub_totals = []
	hide_columns = filters.get("hide_columns")
	dataset = []
	colors = []
	if filters.column_group != "None":
		fields = get_fields(filters)
		for f in fields:
			columns.append(f["label"])
			
			amounts.append(sum(d["{}_amt".format(f["fieldname"])] for d in data))
			#check hide column quantity
			if not hide_columns or  "Transaction" not in hide_columns:
				quantities.append(sum(d["{}_transaction".format(f["fieldname"])] for d in data))

			#check hide column quantity
			if not hide_columns or  "Quantity" not in hide_columns:
				quantities.append(sum(d["{}_qty".format(f["fieldname"])] for d in data))

			#check hide column sub total
			if not hide_columns or  "Sub Total" not in hide_columns:
				sub_totals.append(sum(d["{}_sub_total".format(f["fieldname"])] for d in data))

			#check hide column cost
			if not hide_columns or  "Cost" not in hide_columns:
				costs.append(sum(d["{}_cost".format(f["fieldname"])] for d in data ))
			
			#check hide column profit
			if not hide_columns or  "Profit" not in hide_columns:
				profits.append(sum(d["{}_profit".format(f["fieldname"])] for d in data ))
			
			
		if not hide_columns or  "Transaction" not in hide_columns:
			dataset.append({'name':'Transaction','values':transactions})
			colors.append("#f030fd")

		if not hide_columns or  "Quantity" not in hide_columns:
			dataset.append({'name':'Quantity','values':quantities})
			colors.append("#FF8A65")

		if not hide_columns or  "Sub Total" not in hide_columns:
			dataset.append({'name':'Sub Total','values':sub_totals})
			colors.append("#dd5574")

		if not hide_columns or  "Cost" not in hide_columns:
			dataset.append({'name':'Cost','values':costs})
			colors.append("#1976D2")

		dataset.append({'name':'Amount','values':amounts})
		colors.append("#2E7D32")

		if not hide_columns or  "Profit" not in hide_columns:
			dataset.append({'name':'Profit','values':profits})
			colors.append("#FF3D00")

	else: # if column group is none
		for d in data:
			columns.append(d["row_group"])

		if not hide_columns or  "Transaction" not in hide_columns:
			dataset.append({'name':'Transaction','values':(d["total_transaction"] for d in data)})
			colors.append("#f030fd")

		if not hide_columns or  "Quantity" not in hide_columns:
			dataset.append({'name':"Quantity","values": (d["total_qty"] for d in data)})
			colors.append("#FF8A65")
		#sub total 
		if not hide_columns or  "Sub Total" not in hide_columns:
			dataset.append({'name':"Sub Total","values": (d["sub_total"] for d in data)})
			colors.append("#dd5574")

		if not hide_columns or  "Cost" not in hide_columns:
			dataset.append({'name':"Cost","values": (d["total_cost"] for d in data)})
			colors.append("#1976D2")

		dataset.append({'name':"Amount","values": (d["total_amount"] for d in data)})
		colors.append("#2E7D32")

		if not hide_columns or  "Profit" not in hide_columns:
			dataset.append({'name':"Profit","values": (d["total_profit"] for d in data)})
			colors.append("#FF3D00")


	chart = {
		'data':{
			'labels':columns,
			'datasets':dataset
		},
		"type": filters.chart_type,
		"lineOptions": {
			"regionFill": 1,
		},
		"axisOptions": {"xIsSeries": 1},
		"colors": colors
	}
	return chart

 

def get_row_groups():
	return [
		{
			"fieldname":"a.item_group",
			"label":"Category"
		},
		{
			"fieldname":"a.parent_item_group",
			"label":"Product Group"
		},
		{
			"fieldname":"b.company",
			"label":"Company"
		},
		{
			"fieldname":"ifnull(b.branch,'Not Set')",
			"label":"Branch"
		},
		{
			"fieldname":"ifnull(b.pos_profile,'Not Set')",
			"label":"POS Profile"
		},
		{
			"fieldname":"concat(ifnull(b.customer,'Not Set'),'-',b.customer_name)",
			"label":"Customer"
		},
		{
			"fieldname":"b.customer_group",
			"label":"Customer Group"
		},
		{
			"fieldname":"b.Territory",
			"label":"Territory"
		},
		
		{
			"fieldname":"ifnull(b.set_warehouse,'Not Set')",
			"label":"Warehouse"
		},
		{
			"fieldname":"date_format(b.posting_date,'%%d/%%m/%%Y')",
			"label":"Date"
		},
		{
			"fieldname":"date_format(b.posting_date,'%%m/%%Y')",
			"label":"Month"
		},
		{
			"fieldname":"date_format(b.posting_date,'%%Y')",
			"label":"Year"
		},
		{
			"fieldname":"ifnull(a.brand,'Not Set')",
			"label":"Brand"
		},
		{
			"fieldname":"ifnull(b.membership,'Not Set')",
			"label":"Membership"
		},
		{
			"fieldname":"concat(a.item_code,'-',a.item_name)",
			"label":"Product"
		},
		{
			"fieldname":"ifnull(concat(a.supplier,'-',a.supplier_name),'Not Set')",
			"label":"Supplier"
		},
		{
			"fieldname":"ifnull(a.supplier_group,'Not Set')",
			"label":"Supplier Group"
		},
		{
			"fieldname":"b.selling_price_list",
			"label":"Sale Type"
		},
	]