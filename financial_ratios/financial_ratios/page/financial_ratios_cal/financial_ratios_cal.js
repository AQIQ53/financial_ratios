frappe.pages['financial-ratios-cal'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Financial Ratio Calculator',
		single_column: true
	});
	wrapper = $(wrapper).find('.layout-main-section');
	
	wrapper.append(`
		<div class="container-fluid">
	     	<div class="row">
		      	<div class="col-lg-3 col-md-4 col-sm-12 col-xs-12 company"></div>
		      	<div class="col-lg-3 col-md-4 col-sm-6 col-xs-6 from_date"></div>
		      	<div class="col-lg-3 col-md-4 col-sm-6 col-xs-6 to_date"></div>
	    	</div>
	      <br>
	      <table class="mytab" width='100%'>
	      <!-- Icon Cards-->
          </table>
		</div>
		`);

		

	const [st_year, st_month, st_day] = (frappe.datetime.month_start()).split('-');
	const from_date = [st_day, st_month, st_year].join('-');

	const [end_year, end_month, end_day] = (frappe.datetime.get_today()).split('-')
	const to_date = [end_day, end_month, end_year].join('-')

	var filters = {"company": "Impala Glass Industries Ltd",
	 				"from_date": from_date, "to_date": to_date};

	var make_field = function(class_name, fieldtype, label, options, default_val){
		page[class_name] = frappe.ui.form.make_control({
			df: {
				fieldname: class_name,
				fieldtype: fieldtype,
				label: label,
				options: options,
				onchange: () => {
					var value = null;
					if (fieldtype!='Select'){
						value = $('input[data-fieldname='+class_name+']').val();
					}
					else{
                    value = $("."+class_name).find('.control-value').text();
                  	}
					// else {
					// 	value = $('input[data-fieldname='+class_name+']').text();
					// }

					filters[class_name] = value;
					run(filters.active)
				} 
			},
			get_query: ()=> {
				if(class_name == "customer"){
					return {
						query: "erpnext.controllers.queries.customer_query"
					}
				}
			},
			parent: wrapper.find('.'+class_name),
			render_input: true,
		});
	}
	make_field("company", "Link", "Company", "Company", "Impala Glass Industries Ltd")
	make_field("from_date", "Date", "Start Date", "")
	make_field("to_date", "Date", "End Date", "")

	
	$("input[data-fieldname=company]").val("Impala Glass Industries Ltd")
	$("input[data-fieldname=from_date]").val(from_date)
	$("input[data-fieldname=to_date]").val(to_date)


	var get_finance_ratios = function(){
		frappe.call({
			method: "financial_ratios.financial_ratios.page.financial_ratios_cal.financial_ratios_cal.get_financial_ratios",
			args: {
				'filters': filters
			},
			freeze: true,
			freeze_message: "<p style='color: green'> Getting Balances</p>",
			callback: function(r){
				const data = r.message;
				console.log(data)
				$("#netprofit").html(data["netprofit"])
			}
		})
	}

	var run = function(argu){
		console.log('helllo run function')
		filters["active"] = argu; //its job is to get list data on changing filter
		get_finance_ratios(filters.active);
	}

	get_finance_ratios(filters.active) //to load table data on page loading

	$("#ratio_type").change(function() {
			get_finance_ratios(filters);
		}
	);

	page.set_primary_action('Get Financial Ratios', ()=> run())

}