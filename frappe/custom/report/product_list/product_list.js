// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Product List"] = {
	"filters": [
		{
			fieldname: "warehouse",
			label: "Warehouse",
			fieldtype: "Link",
			options:"Warehouse"
		},
		{
			fieldname: "item_group",
			label: "Item Group",
			fieldtype: "Link",
			options:"Item Group",
		},
		{
			fieldname: "allow_discount",
			label: "Allow Discount",
			fieldtype: "Select",
			default:"All",
			options: [
				   	{"value":"All","description":"All"},
					{"value":"1","description":"Yes"},
					{"value":"0","description":"No"}
				]
		},
	]
};
