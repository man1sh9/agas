import frappe

def run():
	ws = frappe.get_single("Website Settings")
	
	# Clear existing items
	ws.top_bar_items = []
	
	# Standard items
	items = [
		{"label": "Home", "url": "/"},
		{"label": "Events", "url": "/events"},
		{"label": "About", "url": "/about"},
		{"label": "Contact", "url": "/contact"}
	]
	
	for item in items:
		ws.append("top_bar_items", {**item, "right": 0})
	
	# Profile item on the right
	ws.append("top_bar_items", {
		"label": "My Profile",
		"url": "/member_profile",
		"right": 1
	})
	
	ws.save(ignore_permissions=True)
	frappe.db.commit()
	print("Website Navigation updated with Events!")
