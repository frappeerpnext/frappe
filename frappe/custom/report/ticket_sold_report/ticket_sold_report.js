// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ticket Sold Report"] = {
	"filters": [
		{
			fieldname: "start_date",
			label: "Start Date",
			fieldtype: "Date",
			default:frappe.datetime.nowdate()
		},
		{
			fieldname: "end_date",
			label: "End Date",
			fieldtype: "Date",
			default:frappe.datetime.nowdate()
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Item\nSale Invoice\nDate\nCashier",
			"default":"Item"
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group By"),	
			"fieldtype": "Select",
			"options": "None\nDaily\nMonthly\nYearly",
			"default":"None"
		},
	]
};
