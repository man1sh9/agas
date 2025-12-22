import frappe

def run():
	# Check if 'home' Web Page exists
	if frappe.db.exists("Web Page", "home"):
		print("Web Page 'home' exists")
		doc = frappe.get_doc("Web Page", "home")
		print(f"Published: {doc.published}")
		print(f"Route: {doc.route}")
	else:
		print("Web Page 'home' does NOT exist - creating it now")
		
		# Read the HTML content
		with open('/home/frappe/frappe-bench/apps/agas/agas/www/agas_home.html', 'r') as f:
			html_content = f.read()
		
		# Create Web Page
		doc = frappe.get_doc({
			"doctype": "Web Page",
			"title": "Home",
			"route": "home",
			"published": 1,
			"main_section": html_content,
			"main_section_html": html_content
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		print("Web Page 'home' created successfully!")
