# Copyright (c) 2023, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.naming import NamingSeries
from frappe.model.document import Document
from frappe.permissions import get_doctypes_with_read

class ResetDocumentNumber(Document):

	@frappe.whitelist()
	def get_prefixes(self):
		prefixes = self._get_prefixes(['Sales Invoice'])

		return {"prefixes": prefixes}

	def _get_prefixes(self, doctypes) -> list[str]:
		"""Get all prefixes for naming series.

		- For all templates prefix is evaluated considering today's date
		- All existing prefix in DB are shared as is.
		"""
		series_templates = set()
		for d in doctypes:
			try:

				options = frappe.get_meta(d).get_naming_series_options()

				series_templates.update(options)
			except frappe.DoesNotExistError:
				frappe.msgprint(_("Unable to find DocType {0}").format(d))
				continue

		custom_templates = frappe.get_all(
			"DocType",
			fields=["autoname"],
			filters={
				"name": ("not in", doctypes),
				"autoname": ("like", "%.#%"),
				"module": ("not in", ["Core"]),
			},
		)
		if custom_templates:
			series_templates.update([d.autoname.rsplit(".", 1)[0] for d in custom_templates])

		return self._evaluate_and_clean_templates(series_templates)

	def _evaluate_and_clean_templates(self, series_templates: set[str]) -> list[str]:
		evalauted_prefix = set()

		series = frappe.qb.DocType("Series")
		prefixes_from_db = frappe.qb.from_(series).select(series.name).where(series.name == self.main_prefix).run(pluck=True)
		# prefixes_from_db = frappe.qb.from_(series).select(series.name).run(pluck=True)

		evalauted_prefix.update(prefixes_from_db)

		return sorted(evalauted_prefix)

	def validate_set_series(self):
		if not self.prefix:
			frappe.throw(_("Please select prefix"))

	def validate_series_name(self, series):
		NamingSeries(series).validate()

	def set_series_options_in_meta(self, doctype: str, options: str) -> None:
		options = self.get_options_list(options)

		# validate names
		for series in options:
			self.validate_series_name(series)

		if options and self.user_must_always_select:
			options = [""] + options

		default = options[0] if options else ""

		option_string = "\n".join(options)

		self.update_naming_series_property_setter(doctype, "options", option_string)
		self.update_naming_series_property_setter(doctype, "default", default)

		self.naming_series_options = option_string

		frappe.clear_cache(doctype=doctype)


	@frappe.whitelist()
	def update_series_start(self):
		if not self.prefix:
			frappe.throw(_("Please select prefix first"))

		naming_series = NamingSeries(self.prefix)
		previous_value = naming_series.get_current_value()
		naming_series.update_counter(self.counter)

		self.create_version_log_for_change(
			naming_series.get_prefix(), previous_value, self.counter
		)

		frappe.msgprint(
			_("Series counter for {} updated to {} successfully").format(self.prefix, self.counter),
			alert=True,
			indicator="green",
		)
		# self.add_comment(text="""""")
		# self.save()


	def create_version_log_for_change(self, series, old, new):
		version = frappe.new_doc("Version")
		version.ref_doctype = "Series"
		version.docname = series
		version.data = frappe.as_json({"changed": [["current", old, new]]})
		version.flags.ignore_links = True  # series is not a "real" doctype
		version.flags.ignore_permissions = True
		version.insert()


	@frappe.whitelist()
	def get_current(self):
		"""get series current"""
		if self.prefix:
			self.counter = NamingSeries(self.prefix).get_current_value()
		return self.counter
