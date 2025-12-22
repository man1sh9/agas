import frappe

def run():
	# Check Website Settings
	ws = frappe.get_single("Website Settings")
	print(f"Home Page: '{ws.home_page}'")
	print(f"Disable Signup: {ws.disable_signup}")
	
	# Check if index page exists in routes
	from frappe.website.router import get_pages
	pages = get_pages()
	if 'index' in pages:
		print(f"INDEX route found: {pages['index']}")
	else:
		print("INDEX route NOT found")
	
	# List all www files
	import os
	www_path = frappe.get_app_path('agas', 'www')
	if os.path.exists(www_path):
		files = os.listdir(www_path)
		print(f"Files in www: {files}")
