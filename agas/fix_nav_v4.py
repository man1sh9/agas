import frappe

def run():
	ws = frappe.get_single("Website Settings")
	ws.top_bar_items = []
	ws.append("top_bar_items", {"label": "Home", "url": "/", "right": 0})
	ws.append("top_bar_items", {"label": "About", "url": "/about", "right": 0})
	ws.append("top_bar_items", {"label": "Contact", "url": "/contact", "right": 0})
	ws.append("top_bar_items", {"label": "My Profile", "url": "/member_profile", "right": 1})
	ws.save(ignore_permissions=True)
	frappe.db.commit()
