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
	branches = frappe.db.get_list('Branch', pluck='name')
	if event in ["on_change","on_update","after_insert"]:
		event = "on_update"

	for b in branches:
		if not frappe.db.exists("Data for Sync", [
			{"branch": b},
			{"is_sync":0},
			{"doc_type":doctype},
			{"doc_name":name},
			{"transaction_type": event}
		]):
			obj = frappe.get_doc({
				"doctype":"Data for Sync",
				"branch" : b,
				'doc_type': doctype,
				'doc_name': name,
				"transaction_type":event,
				"is_sync":0
			})
			obj.insert()
		

 