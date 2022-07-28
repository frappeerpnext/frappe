# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DataforSync(Document):
	pass

@frappe.whitelist()
def notify_sync(doc, event):
	notify_docs = ["Item","Item Group","Item Price","Customer","Customer Group" ,"User","POS Profile","Company","System Settings","Currency Exchange","Warehouse" ,"Membership Type"]
	"""called via hooks"""
	if doc.doctype in notify_docs:
	 	 notify_sync_job(doc.doctype,doc.name,event)


@frappe.whitelist()
def notify_sync_job(doctype,name, event):
	return
	
	branches = frappe.db.get_list('Branch', pluck='name')
	if event in ["on_change","on_update","after_insert"]:
		event = "on_update"

	for b in branches:
		frappe.db.sql(
			"""
			DELETE FROM `tabData for Sync`
			WHERE 
				branch=%s and 
				doc_type = %s and 
				doc_name = %s and 
				transaction_type =%s and 
				is_sync=0
			""",
			(b,doctype,name,event)
		)

		obj = frappe.get_doc({
			"doctype":"Data for Sync",
			"branch" : b,
			'doc_type': doctype,
			'doc_name': name,
			"transaction_type":event,
			"is_sync":0
		})
		obj.insert()
		

@frappe.whitelist()
def delete_synced_record(name):
	frappe.delete_doc('Data for Sync', name)
	frappe.db.commit()

@frappe.whitelist()
def get_synced_record(name):
	frappe.delete_doc('Data for Sync', name)
	frappe.db.commit()



 