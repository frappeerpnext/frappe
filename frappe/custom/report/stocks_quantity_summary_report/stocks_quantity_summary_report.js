// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stocks Quantity Summary Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options:"Company",
			default:frappe.defaults.get_user_default("Company"),
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse', txt,{"is_group":0});
			}
		},
		{
			"fieldname": "item_group",
			"label": __("Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Item Group', txt,{"is_group":1});
			}
		},
		{
			"fieldname": "item_category",
			"label": __("Category"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Item Group', txt,{"is_group":0});
			}
		},
		{
			"fieldname": "show_columns",
			"label": __("Show Columns"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Reserved Quantity","description":"Reserved Quantity"},
					{"value":"Requested Quantity","description":"Request Quantity"},
					{"value":"Ordered Quantity","description":"Ordered Quantity"},
					{"value":"Total Cost","description":"Total Cost"}					
				]
			},
			"default":"All"
		},
		{
			fieldname: "limit",
			label: "Show Record",
			fieldtype: "Int",
			default:50
		},
	],
	onload: function(report) {
		setTimeout(() => {
			x = document.getElementsByClassName("page-content")[0];
			x.classList.add('grid-column-br');
		}, 5000);
		
	}
	
};

