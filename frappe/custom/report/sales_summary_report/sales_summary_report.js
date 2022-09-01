// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Summary Report"] = {
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
			default:frappe.datetime.month_start()
		},
		{
			fieldname: "end_date",
			label: "End Date",
			fieldtype: "Date",
			default:frappe.datetime.month_end()
		},
		{
			"fieldname": "price_list",
			"label": __("Sale Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Price List', txt,{"selling":1});
			}
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
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Product\nCategory\nProduct Group\nBrand\nCompany\nBranch\nSale Type\nPOS Profile\nCustomer\nCustomer Group\nMembership\nTerritory\nSupplier\nSupplier Group\nWarehouse\nDate\n\Month\nYear",
			"default":"Category"
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group By"),
			"fieldtype": "Select",
			"options": "None\nDaily\nWeekly\nMonthly\nQuarterly\nHalf Yearly\nYearly",
			"default":"None"
		},
		{
			"fieldname": "hide_columns",
			"label": __("Hide Columns"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Quantity","description":"Quantity"},
					{"value":"Sub Total","description":"Sub Total"},
					{"value":"Cost","description":"Cost"},
					{"value":"Profit","description":"Profit"},
				]
			},
			"default":"All"
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline",
			"d,efault":"bar"
		}
	]
};

 