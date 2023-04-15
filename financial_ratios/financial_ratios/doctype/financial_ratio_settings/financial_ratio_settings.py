# Copyright (c) 2023, Aqiq Solutions Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr
class FinancialRatioSettings(Document):
	
	def validate(self):
		# get_financial_ratios(self.company, self.from_date, self.to_date, self.ratios)
		conditions = ""

		if self.company:
			conditions += f""" and company='{self.company}'"""
		if self.from_date:
			conditions += f""" and posting_date>='{self.from_date}'"""
		if self.to_date:
			conditions += f""" and posting_date<='{self.to_date}'"""

		for d in self.ratios:
			if d.based_on == 'Root Account':
				if frappe.db.exists('Account', d.divisor):
					lft_rgt_divisor = frappe.db.get_value('Account', {'name': d.divisor}, ['lft', 'rgt'])
		
					divisor_balance = round(frappe.db.sql("""select SUM(debit) - SUM(credit) from `tabGL Entry`
							where is_cancelled=0
							and account in (SELECT name from `tabAccount` where lft>=%s and rgt<=%s) %s"""%(lft_rgt_divisor[0], lft_rgt_divisor[1], conditions), debug=False)[0][0], 2)	
				else:
					frappe.throw(f"The selected account {d.divisor} does not exist in chart of accounts.")

				if frappe.db.exists('Account', d.dividend):
					lft_rgt_dividend = frappe.db.get_value('Account', {'name': d.dividend}, ['lft', 'rgt'])
					
					dividend_balance = round(frappe.db.sql("""select SUM(credit) - SUM(debit) from `tabGL Entry`
							where is_cancelled=0
							and account in (SELECT name from `tabAccount` where lft>=%s and rgt<=%s) %s"""%(lft_rgt_dividend[0], lft_rgt_dividend[1], conditions), debug=False)[0][0], 2)
				else:
					frappe.throw(f"The selected account {d.dividend} does not exist in chart of accounts.")	

				""" Calculate ratios here """
				this_ratio = (divisor_balance or 0.0)/(dividend_balance or 1.0)
				d.divisor_value = divisor_balance
				d.dividend_value = dividend_balance
				d.ratio_value = this_ratio

			if d.based_on == 'Account Type':
				if frappe.db.exists('Account', {'account_type' : d.divisor}):
					accounts_divisor = frappe.db.get_list('Account', {'account_type': d.divisor}, pluck='name')

					divisor_balance = round(frappe.db.sql("""select SUM(debit) - SUM(credit) from `tabGL Entry`
							where is_cancelled=0
							and account in {} {}""".format(tuple(accounts_divisor), conditions), debug=False)[0][0], 2)
				else:
					frappe.throw(f"There are no accounts for the selected Account Type {d.divisor} or may be the selected Account Type is wrong!")	


				if frappe.db.exists('Account', {'account_type' : d.dividend}):
					accounts_dividend = frappe.db.get_list('Account', {'account_type': d.dividend}, pluck='name')
					
					dividend_balance = round(frappe.db.sql("""select SUM(credit) - SUM(debit) from `tabGL Entry`
							where is_cancelled=0
							and account in {} {}""".format(tuple(accounts_dividend), conditions), debug=False)[0][0], 2)
				else:
					frappe.throw(f"There are no accounts for the selected Account Type {d.dividend} or may be the selected Account Type is wrong!")

				""" Calculate ratios here """
				this_ratio = (divisor_balance or 0.0)/(dividend_balance or 1.0)
				d.divisor_value = divisor_balance
				d.dividend_value = dividend_balance
				d.ratio_value = this_ratio
