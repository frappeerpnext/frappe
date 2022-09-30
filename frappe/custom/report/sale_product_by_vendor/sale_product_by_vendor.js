// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sale Product By Vendor"] = {
	"filters": [
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options:"Company",
			default:frappe.defaults.get_user_default("Company"),
		},
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
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				
				return frappe.db.get_link_options('Item Group', txt,{"is_group":1});
			}
		},
		{
			"fieldname": "item_category",
			"label": __("Item Category"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				group = frappe.query_report.get_filter_value("item_group");
				if(group==""){
					return frappe.db.get_link_options('Item Group', txt,filters={
						is_group:0
					});
				}
				else {
					return frappe.db.get_link_options('Item Group', txt,filters={
						is_group:0,
						"parent_item_group":["in",group]
					});
				}
			}
		},
		{
			fieldname: "warehouse",
			label: "Warehouse",
			fieldtype: "Link",
			options:"Warehouse",
			filters:{"is_group":0}
		},
		{
			"fieldname": "supplier_group",
			"label": __("Supplier Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				
				return frappe.db.get_link_options('Supplier Group', txt,{"is_group":0});
			}
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				group = frappe.query_report.get_filter_value("supplier_group");
				if(group==""){
					return frappe.db.get_link_options('Supplier', txt);
				}
				else {
					return frappe.db.get_link_options('Supplier', txt,filters={
						"supplier_group":["in",group]
					});
				}
			}
		},
		{
			fieldname: "not_set_supplier",
			label: "Not Set",
			fieldtype: "Check"
		},
	],
	"formatter": function(value, row, column, data, default_formatter) {
	
		value = default_formatter(value, row, column, data);

		if (data && data.is_group==1) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
};
