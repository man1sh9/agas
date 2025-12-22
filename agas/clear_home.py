import frappe

def run():
	frappe.db.set_single_value('Website Settings', 'home_page', '')
	frappe.db.commit()
	print("Home page setting cleared")
