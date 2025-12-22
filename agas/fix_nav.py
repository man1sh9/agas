import frappe

def run():
	ws = frappe.get_single("Website Settings")
	
	# Clear existing items
	ws.top_bar_items = []
	
	# Add new correct items
	# 1. Home
	ws.append("top_bar_items", {
		"label": "Home",
		"url": "/",
		"right": 0
	})
	
	# 2. About
	ws.append("top_bar_items", {
		"label": "About",
		"url": "/about",
		"right": 0
	})
	
	# 3. Contact
	ws.append("top_bar_items", {
		"label": "Contact",
		"url": "/contact",
		"right": 0
	})
	
	ws.save(ignore_permissions=True)
	frappe.db.commit()
	print("Website Navigation updated successfully!")
