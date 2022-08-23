
import frappe

from frappe import _, whitelist

no_cache = 1

@frappe.whitelist()
def get_item(name):
	return frappe.get_doc("Item",name)
