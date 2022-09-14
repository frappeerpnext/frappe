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
					{"value":"Quantity Sold Yesterday","description":"Quantity Sold Yesterday"},
					{"value":"Quantity Sold Last 7 Days","description":"Quantity Sold Last 7 Days"},
					{"value":"Quantity Sold Last 14 Days","description":"Quantity Sold Last 14 Days"},
					{"value":"Quantity Sold Last 30 Days","description":"Quantity Sold Last 30 Days"},
					{"value":"Quantity Purchase Yesterday","description":"Quantity Purchase Yesterday"},
					{"value":"Quantity Purchase Last 7 Days","description":"Quantity Purchase Last 7 Days"},
					{"value":"Quantity Purchase Last 14 Days","description":"Quantity Purchase Last 14 Days"},
					{"value":"Quantity Purchase Last 30 Days","description":"Quantity Purchase Last 30 Days"},
					{"value":"Quantity Receive Yesterday","description":"Quantity Receive Yesterday"},
					{"value":"Quantity Receive Last 7 Days","description":"Quantity Receive Last 7 Days"},
					{"value":"Quantity Receive Last 14 Days","description":"Quantity Receive Last 14 Days"},
					{"value":"Quantity Receive Last 30 Days","description":"Quantity Receive Last 30 Days"},
				]
			},
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
