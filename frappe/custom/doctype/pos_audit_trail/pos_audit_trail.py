# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class POSAuditTrail(Document):
	def validate(self):
		if self.is_new():
			if self.id:
				if frappe.db.exists("POS Audit Trail", {"id": self.id}):
					frappe.throw(
						_("POS Audit Trail id {} already exist".format(self.id))
					)
