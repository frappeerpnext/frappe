// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["POS Invoice Payment Type Breakdown"] = {
	"filters": [
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options:"Company",
			default:frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "department",
			label: "Department",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				console.log(frappe.user.get_data('Department'))
				return frappe.db.get_link_options('Department', txt, {"name": ['!=', 'All Departments']});
				
			},
			 
		},
		{
			fieldname: "branch",
			label: "Branch",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Branch', txt);
			}
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
	]
};
