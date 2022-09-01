// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sale Transaction"] = {
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
			fieldname: "customer",
			label: "Customer",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Customer', txt);
			}
		},
		{
			fieldname: "price_list",
			label: "Sale Type",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Price List', txt,{"selling":1});
			}
		},
	]
};
