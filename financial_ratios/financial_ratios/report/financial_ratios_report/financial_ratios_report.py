# Copyright (c) 2023, Aqiq Solutions Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr

def execute(filters=None):
	columns, data = get_columns(), []

	conditions = get_conditions(filters)

	financial_ratio_settings_doc = frappe.get_doc('Financial Ratio Settings', 'Financial Ratio Settings')
	for d in financial_ratio_settings_doc.ratios:
		row = frappe._dict()
		if d.based_on == 'Root Account':
			if frappe.db.exists('Account', d.divisor):
				lft_rgt_divisor = frappe.db.get_value('Account', {'name': d.divisor}, ['lft', 'rgt'])
				divisor_balance = frappe.db.sql("""select SUM(debit) - SUM(credit) from `tabGL Entry`
						where is_cancelled=0
						and account in (SELECT name from `tabAccount` where lft>=%s and rgt<=%s) %s"""%(lft_rgt_divisor[0], lft_rgt_divisor[1], conditions), debug=False)[0][0]
				divisor_balance = round(divisor_balance if divisor_balance else 0.0, 2)	
			else:
				frappe.throw(f"The selected account {d.divisor} does not exist in chart of accounts.")

			if frappe.db.exists('Account', d.dividend):
				lft_rgt_dividend = frappe.db.get_value('Account', {'name': d.dividend}, ['lft', 'rgt'])
				dividend_balance = frappe.db.sql("""select SUM(credit) - SUM(debit) from `tabGL Entry`
						where is_cancelled=0
						and account in (SELECT name from `tabAccount` where lft>=%s and rgt<=%s) %s"""%(lft_rgt_dividend[0], lft_rgt_dividend[1], conditions), debug=False)[0][0]
				dividend_balance = round(dividend_balance if dividend_balance else 1.0, 2)
			else:
				frappe.throw(f"The selected account {d.dividend} does not exist in chart of accounts.")	

			""" Calculate ratios here """
			this_ratio = (divisor_balance or 0.0)/(dividend_balance or 1.0)
			row.ratio_type = d.ratio_type
			row.based_on = d.based_on
			row.divisor = d.divisor
			row.dividend = d.dividend
			row.divisor_value = divisor_balance
			row.dividend_value = dividend_balance
			row.ratio_value = this_ratio

		if d.based_on == 'Account Type':
			if frappe.db.exists('Account', {'account_type' : d.divisor}):
				accounts_divisor = frappe.db.get_list('Account', {'account_type': d.divisor}, pluck='name')
				divisor_balance = frappe.db.sql("""select SUM(debit) - SUM(credit) from `tabGL Entry`
						where is_cancelled=0
						and account in {} {}""".format(tuple(accounts_divisor), conditions), debug=False)[0][0]
				divisor_balance = round(divisor_balance if divisor_balance else 0.0, 2)
			else:
				frappe.throw(f"There are no accounts for the selected Account Type {d.divisor} or may be the selected Account Type is wrong!")	


			if frappe.db.exists('Account', {'account_type' : d.dividend}):
				accounts_dividend = frappe.db.get_list('Account', {'account_type': d.dividend}, pluck='name')
				dividend_balance = frappe.db.sql("""select SUM(credit) - SUM(debit) from `tabGL Entry`
						where is_cancelled=0
						and account in {} {}""".format(tuple(accounts_dividend), conditions), debug=False)[0][0]
				dividend_balance = round(dividend_balance if dividend_balance else 1.0, 2)
			else:
				frappe.throw(f"There are no accounts for the selected Account Type {d.dividend} or may be the selected Account Type is wrong!")

			""" Calculate ratios here """
			this_ratio = (divisor_balance or 0.0)/(dividend_balance or 1.0)
			row.ratio_type = d.ratio_type
			row.based_on = d.based_on
			row.divisor = d.divisor
			row.dividend = d.dividend
			row.divisor_value = divisor_balance
			row.dividend_value = dividend_balance
			row.ratio_value = this_ratio
		data.append(row)
	return columns, data

def get_conditions(filters):
	conditions = ""

	if filters.get("company"):
		conditions += f""" and company='{filters.get('company')}'"""
	if filters.get("from_date"):
		conditions += f""" and posting_date>='{filters.get("from_date")}'"""
	if filters.get("to_date"):
		conditions += f""" and posting_date<='{filters.get("to_date")}'"""
	return conditions


def get_columns():
	return [
		{
			'fieldname': 'ratio_type',
			'fieldtype': 'Select',
			'options': ['Current Ratio', 'Return on Equity', 'Gross Profit Margin', 'Price Earnings', 'Inventory Turnover', \
			'Days Sales of Inventory', 'Fixed Assets Turnover', 'Return on Assets', 'Asset Turnover'],
			'label': _('Ratio'),
			'width': 200,
		},
		{
			'fieldname': 'based_on',
			'fieldtype': 'Data',
			'options': ['Root Account', 'Account Type'],
			'label': _('Based On'),
			'width': 200,
		},
		{
			'fieldname': 'divisor',
			'fieldtype': 'Data',
			'label': _('Divisor'),
			'width': 280,
		},
		{
			'fieldname': 'dividend',
			'fieldtype': 'Data',
			'label': _('Dividend'),
			'width': 280,
		},
		{
			'fieldname': 'divisor_value',
			'fieldtype': 'Float',
			'label': _('Divisor Value'),
			'width': 200,
		},
		{
			'fieldname': 'dividend_value',
			'fieldtype': 'Float',
			'label': _('Dividend Value'),
			'width': 200,
		},
		{
			'fieldname': 'ratio_value',
			'fieldtype': 'Float',
			'label': _('Ratio Value'),
			'width': 150,
		},

	]