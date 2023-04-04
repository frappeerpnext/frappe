# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
	strip_html,
)
from frappe.utils.html_utils import clean_html

class DataforSync(Document):
	pass


@frappe.whitelist()
def notify_sync(doc, event):
	
	#settings = frappe.get_doc('System Settings')
	#if not settings.disable_data_for_sync_notify:
	notify_docs = ["Item","Item Group","Item Price","Customer","Customer Group" ,"User","POS Profile","Company","System Settings","Currency Exchange","Warehouse" ,"Membership Type","Tag","POS Config","POS Prices Rule",'Price List',"Comment","POS Menu"]
 
	"""called via hooks"""
	if doc.doctype =="Comment" :
		if doc.content:
			if "renamed from" in doc.content:
				notify_sync_job(doc.reference_doctype,strip_html(doc.content.replace("renamed from","")),"on_renamed")
				
	else:
		if doc.doctype in notify_docs:
			if doc.doctype=='Item Price':
				notify_sync_job("Item",doc.item_code,event)
			else:
				notify_sync_job(doc.doctype,doc.name,event)


@frappe.whitelist()
def notify_sync_job(doctype,name, event):
	branches = frappe.db.get_list('Branch',filters={'disable_from_sync': 0}, pluck='name')
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
				transaction_type =%s
			""",
			(b,doctype,name,event)
		)

		obj = frappe.get_doc({
			"doctype":"Data for Sync",
			"branch" : b,
			'doc_type': doctype,
			'doc_name': name,
			"transaction_type":event
		})
		obj.insert()
		

@frappe.whitelist()
def delete_synced_record(name):
	frappe.db.sql("""DELETE FROM `tabData for Sync` WHERE branch = 'Stores - LA'""")
	frappe.db.sql("""DELETE FROM `tabData for Sync` WHERE name =%s""",(name))
	frappe.db.commit()

@frappe.whitelist()
def delete_data_for_sync_record(branch_name):
	frappe.db.sql("""DELETE FROM `tabData for Sync` WHERE branch = 'Stores - LA'""")
	frappe.db.sql("""DELETE FROM `tabData for Sync` WHERE branch =%s""",(branch_name))
	frappe.db.commit()
	return "Done"
	



@frappe.whitelist()
def get_synced_record(name):
	frappe.delete_doc('Data for Sync', name)
	frappe.db.commit()


