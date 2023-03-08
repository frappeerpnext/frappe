// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales List"] = {
	"filters": [
		{
			fieldname: "date",
			label: "Date",
			fieldtype: "Date",
			default:frappe.datetime.nowdate()
		}
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
