// Copyright (c) 2023, Aqiq Solutions Ltd and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Financial Ratios Report"] = {
	"filters": [
		{
			'fieldname': 'company',
			'fieldtype': 'Link',
			'options': 'Company',
			'label': __('Company'),
			'default': frappe.defaults.get_default('company'),
			'width': 200
		},
		{
			'fieldname': 'from_date',
			'fieldtype': 'Date',
			'label': __('From Date'),
			'width': 200
		},
		{
			'fieldname': 'to_date',
			'fieldtype': 'Date',
			'label': __('To Date'),
			'width': 200
		},

	]
};
