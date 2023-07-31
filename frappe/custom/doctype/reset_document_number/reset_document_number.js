// Copyright (c) 2023, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Reset Document Number', {
	refresh: function(frm) {
		frm.trigger("setup_transaction_autocomplete");
		frappe.call({
			method: "get_current",
			doc: frm.doc,
			callback: function(r) {
				frm.refresh_field("counter");
			},
		});
		

	},
	setup_transaction_autocomplete: function(frm) {
		frappe.call({
			method: "get_prefixes",
			doc: frm.doc,
			callback: function(r) {
				frm.fields_dict.prefix.set_data(r.message.prefixes);
			},
		});
	},
	prefix: function(frm) {
		frappe.call({
			method: "get_current",
			doc: frm.doc,
			callback: function(r) {
				frm.refresh_field("counter");
			},
		});
	},
});
