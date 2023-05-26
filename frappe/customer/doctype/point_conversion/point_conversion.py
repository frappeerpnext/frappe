# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PointConversion(Document):
	def before_save(self):
		if len(self.payment_type)>0:
				payment_type_list = self.payment_type
				str_json = ""
				for x in payment_type_list:
					str_json += str(PointPaymentModel(x.payment_type).__dict__)+ ","
				str_json ="[" + str_json[0:len(str_json)-1] + "]"
				self.allow_payment_type_data = str_json
		else:
			self.allow_payment_type_data = ""
	
class PointPaymentModel:
	def __init__(self, payment_type):
		self.payment_type = payment_type
