import frappe

def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/auth"
		raise frappe.Redirect
	
	context.no_cache = 1
	# Pre-fill data
	profile = frappe.db.get_value("Member Profile", {"user": frappe.session.user}, "*", as_dict=True) or {}
	context.member_data = profile
	
	# Fetch upcoming published events for the dropdown
	today = frappe.utils.getdate()
	context.events = frappe.get_all("Agas Event", 
		filters={
			"published": 1,
			"event_start_date": [">=", today],
		},
		fields=["title", "event_start_date", "event_end_date"], 
		order_by="event_start_date asc"
	)

	# Check for URL parameter ?event=XYZ
	selected_event = frappe.form_dict.get("event")
	context.selected_event = selected_event

	# Find selected event details to pass for defaults
	context.current_event_dates = {}
	if selected_event:
		ev_dates = frappe.db.get_value("Agas Event", selected_event, ["event_start_date", "event_end_date"], as_dict=True)
		if ev_dates:
			context.current_event_dates = ev_dates

	# Fetch existing registration if exists
	context.registration_data = {}
	if selected_event and profile.get("name"):
		reg = frappe.get_all("Event Registration",
			filters={"user": frappe.session.user, "event": selected_event},
			fields=["*"],
			limit=1
		)
		if reg:
			reg = reg[0]
			# Fetch child table members
			reg["visitor_members"] = frappe.get_all("Event Registration Member",
				filters={"parent": reg.name},
				fields=["*"],
				order_by="creation asc"
			)
			# Fetch food schedule
			food_schedule = frappe.get_all("Event Food Day",
				filters={"parent": reg.name},
				fields=["date", "breakfast", "lunch", "dinner"],
				order_by="date asc"
			)
			# Convert dates to strings for JSON serialization in template
			for day in food_schedule:
				if day.get("date"):
					day["date"] = str(day["date"])
			reg["food_schedule"] = food_schedule
			context.registration_data = reg

	# Fetch Family Members
	if profile.get("name"):
		context.family_members = frappe.get_all("Family Member",
			filters={"primary_member": profile.name},
			fields=["*"],
			order_by="sr_no asc"
		)
	else:
		context.family_members = []

	# Read-only logic
	is_read_only = False
	if frappe.form_dict.get("view") == "1":
		is_read_only = True
	
	if selected_event:
		event_end_date = frappe.db.get_value("Agas Event", selected_event, "event_end_date")
		if event_end_date and frappe.utils.getdate(event_end_date) < frappe.utils.getdate():
			is_read_only = True
			
	context.is_read_only = is_read_only
	context.csrf_token = frappe.session.csrf_token
