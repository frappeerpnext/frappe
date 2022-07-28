# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TempChildTableDataImport(Document):
	
	def after_insert(self):
		if self.parent_doctype=="Item" and self.doctype_name=="Item Barcode":
			add_barcode_to_item(self)
		elif self.parent_doctype=="Item" and self.doctype_name=="UOM Conversion Detail":
			add_unit_to_item(self)
		elif self.parent_doctype=="Item" and self.doctype_name=="Branch Items":
			update_item_availability(self)

def add_barcode_to_item(self):
	doc = frappe.get_doc(self.parent_doctype,self.doc_name)
	doc.append("barcodes", {
                "barcode":self.barcode,
                "uom":self.uom,
            })
	doc.save(
		ignore_permissions=True, # ignore write permissions during insert
    	ignore_version=True 
	)
	frappe.db.commit()


def add_unit_to_item(self):
	doc = frappe.get_doc(self.parent_doctype,self.doc_name)
	doc.append("uoms", {
                "conversion_factor":self.conversion_factor,
                "uom":self.uom,
            })
	doc.save(
		ignore_permissions=True, # ignore write permissions during insert
    	ignore_version=True 
	)
	frappe.db.commit()

def update_item_availability(self):
	doc = frappe.get_doc(self.parent_doctype,self.doc_name)
	doc.branches =[]
	for b in self.branches.split(","):
		code =   frappe.db.get_value('Branch', b, 'branch_code')
		doc.append("branches", {
					"branch":b,
					"branch_code":code
				})
				
	doc.save(
		ignore_permissions=True, # ignore write permissions during insert
    	ignore_version=True 
	)
	frappe.db.commit()


