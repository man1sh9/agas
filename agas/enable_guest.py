import frappe

def run():
	# Update Website Settings to allow guest access
	ws = frappe.get_single("Website Settings")
	ws.disable_signup = 0
	ws.home_page = ""
	ws.save(ignore_permissions=True)
	frappe.db.commit()
	print("Website Settings updated - guest access enabled, home_page cleared")
