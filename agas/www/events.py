import frappe
from frappe.utils import nowdate

def get_context(context):
	context.no_cache = 1
	# Fetch upcoming events
	context.upcoming_events = frappe.get_all("Agas Event", 
		filters={"published": 1, "event_start_date": [">=", nowdate()]},
		fields=["title", "subtitle", "event_start_date", "event_end_date", "venue", "image", "description"],
		order_by="event_start_date asc"
	)
	
	# Fetch past events
	context.past_events = frappe.get_all("Agas Event", 
		filters={"published": 1, "event_start_date": ["<", nowdate()]},
		fields=["title", "subtitle", "event_start_date", "event_end_date", "venue", "image", "description"],
		order_by="event_start_date desc"
	)
