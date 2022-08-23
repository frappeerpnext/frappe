
frappe.pages['item-detail'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

MyPage = Class.extend({
	init: function(wrapper) {
   		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'My Super Pagexxx',
			single_column: true,
			
		});
		this.page.set_indicator('Pending', 'orange');
		this.page.set_title_sub("product name detal page");

		this. page.set_primary_action('New', () => alert_me(this.page), 'octicon octicon-plus')
		this. page.set_secondary_action('Refresh', () => alert_me(this.page), 'octicon octicon-plus')
		this.page.add_menu_item('Send Email', () => alert_me(this.page));

		this.page.add_action_item('Delete', () => open_dialog());

		this.page.add_field({
			label: 'Status',
			fieldtype: 'Select',
			fieldname: 'status',
			options: [
				'Open',
				'Closed',
				'Cancelled'
			],
			change() {
				console.log(field.get_value());
			}
		});
		
		frappe.breadcrumbs.add("Stock");
		
	 
		
		this.make();
		this.item = get_item("114477");
		},
		make: function() {

			$(frappe.render_template("item_detail",this.item)).appendTo(this.page.main);
			
		}
		 
}
)


var get_item =function(name)  {
	frappe.xcall('frappe.custom.page.item_detail.item_detail.get_item', {
		name: name
	}).then((r) => {
		frappe.msgprint(r.item_name);
		return r;
	});

}

var alert_me=function(page){
	frappe.msgprint("Hello world");
	page.set_indicator('Submited', 'green');
	page.add_inner_button('Update Posts',()=>{}, "Make");
	let values = page.get_form_values();
	console.log(values);
	frappe.msgprint(values.status);

}

var open_dialog = function(){
	let d = new frappe.ui.Dialog({
		title: 'Enter details',
		fields: [
			{
				label: 'First Name',
				fieldname: 'first_name',
				fieldtype: 'Link',
				options: "Item"
			},
			{
				label: 'Last Name',
				fieldname: 'last_name',
				fieldtype: 'Data'
			},
			{
				label: 'Age',
				fieldname: 'age',
				fieldtype: 'Int'
			}
		],
		primary_action_label: 'Submit',
		primary_action(values) {
			console.log(values);
			d.hide();
		}
	});
	
	d.show();
}

