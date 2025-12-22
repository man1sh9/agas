import frappe

def get_context(context):
	if frappe.session.user != "Guest":
		frappe.local.login_manager.logout()
	
	# Throwing the redirect exception is the most reliable way 
	# to prevent getting a JSON response from Frappe.
	frappe.redirect("/")
