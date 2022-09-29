// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Product Qty Report"] = {
	"filters": [
		{
			fieldname: "branch",
			label: "Branch",
			fieldtype: "Link",
			options:"Branch",
			reqd:1
		},
		{
			fieldname: "warehouse",
			label: "Warehouse",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse', txt,{"is_group":0});
			}
		},
		{
			fieldname: "item_group",
			label: "Item Group",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Item Group', txt,{"is_group":0});
			}
		},
		{
			fieldname: "supplier",
			label: "Supplier",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Supplier', txt);
			}
		},
		{
			fieldname: "keyword",
			label: "Keyword",
			fieldtype: "Data",
		},
		{
			"fieldname": "show_columns",
			"label": __("Show Columns"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
				 
					{"value":"Reorder Level","description":"Reorder Level"},
					{"value":"Reorder Quantity","description":"Reorder Quantity"},
					{"value":"Reserved Quantity","description":"Reserved Quantity"},
					{"value":"Ordered Quantity","description":"Ordered Quantity"},
					{"value":"Requested Quantity","description":"Requested Quantity"},
					{"value":"Quantity Sold","description":"Quantity Sold Yesterday"},
					{"value":"Quantity Purchase","description":"Quantity Purchase Yesterday"},
					{"value":"Quantity Receive","description":"Quantity Receive Yesterday"},
				]
			},
		},
		{
			fieldname: "start_date",
			label: "Start Date",
			fieldtype: "Date",
			default:frappe.datetime.get_today()
		},
		{
			fieldname: "end_date",
			label: "End Date",
			fieldtype: "Date",
			default:frappe.datetime.get_today()
		},
		{
			fieldname: "top",
			label: "Show record",
			fieldtype: "Int",
			default:50,
			reqd:1
		},
	],
	 
};
