import frappe

def run():
	ws = frappe.get_single("Website Settings")
	print("--- Top Bar Items ---")
	for item in ws.top_bar_items:
		print(f"Label: {item.label}, URL: {item.url}, Parent: {item.parent_label}")

	print("\n--- Portal Menu Items ---")
	# Portal Settings usually controls the sidebar/menu for logged-in users
	if frappe.db.exists("Portal Settings", "Portal Settings"):
		ps = frappe.get_single("Portal Settings")
		if hasattr(ps, 'menu'):
			for item in ps.menu:
				print(f"Label: {item.title}, Route: {item.route}")
		else:
			print("Portal Settings has no 'menu' field or is empty.")
