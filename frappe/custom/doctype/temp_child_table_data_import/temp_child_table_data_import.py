# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TempChildTableDataImport(Document):
	
	def after_insert(self):
		if self.parent_doctype=="Item" and self.doctype_name=="Item Barcode":
			add_barcode_to_item(self)


def add_barcode_to_item(self):
	doc = frappe.get_doc(self.parent_doctype,self.doc_name)
	doc.barcodes
	doc.append("barcodes", {
                "barcode":self.barcode,
                "uom":self.uom,
            })
	doc.save()
	frappe.db.commit()

	
