// Copyright (c) 2023, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item List', {
	purchase_order:function(frm){
		frm.clear_table("items");
		frm.doc.purchase_invoice = ""
		frm.refresh_field('purchase_invoice');
		frappe.model.with_doc("Purchase Order", frm.doc.purchase_order, function() {
            var tabletransfer= frappe.model.get_doc("Purchase Order", frm.doc.purchase_order)
            $.each(tabletransfer.items, function(index, row){
				frm.add_child('items', {
					item: row.item_code,
					copies: 1
					});
				frm.refresh_field('items');
            });
        });
	},
	purchase_invoice:function(frm){
		frm.clear_table("items");
		frm.doc.purchase_order = ""
		frm.refresh_field('purchase_order');
		frappe.model.with_doc("Purchase Invoice", frm.doc.purchase_invoice, function() {
            var tabletransfer= frappe.model.get_doc("Purchase Invoice", frm.doc.purchase_invoice)
            $.each(tabletransfer.items, function(index, row){
				frm.add_child('items', {
					item: row.item_code,
					copies: 1
					});
				frm.refresh_field('items');
            });
        });
	}
});
