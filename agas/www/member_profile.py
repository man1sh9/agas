import frappe

def get_context(context):
	print("DEBUG: member_profile.py get_context called")
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/auth"
		raise frappe.Redirect
	
	context.no_cache = 1
	# Fetch existing profile if it exists
	profile = frappe.get_all("Member Profile", 
		filters={"user": frappe.session.user}, 
		fields=["*"], 
		limit=1
	)
	profile = profile[0] if profile else None
	
	# If no profile, provide initial data from User record
	if not profile:
		user_doc = frappe.get_doc("User", frappe.session.user)
		profile = {
			"first_name": user_doc.first_name,
			"last_name": user_doc.last_name,
			"email_id": user_doc.email,
			"mobile_no": user_doc.mobile_no
		}
	
	context.member_data = profile
	
	# Fetch family members
	if profile.get("name"):
		context.family_members = frappe.get_all("Family Member", 
			filters={"primary_member": profile.name},
			fields=["*"],
			order_by="sr_no asc"
		)
	else:
		context.family_members = []

	context.csrf_token = frappe.session.csrf_token

	# Fetch event registrations
	registrations = frappe.get_all("Event Registration",
		filters={"user": frappe.session.user},
		fields=["name", "event", "status", "no_of_visitors", "check_in_date", "creation"]
	)

	upcoming_events = []
	past_events = []
	today = frappe.utils.getdate()

	for reg in registrations:
		# Fetch event dates from Agas Event
		event_dates = frappe.db.get_value("Agas Event", reg.event, ["event_start_date", "event_end_date"], as_dict=True)
		if not event_dates:
			continue
			
		reg.event_date = event_dates.event_start_date
		end_date = event_dates.event_end_date
		
		if end_date and frappe.utils.getdate(end_date) >= today:
			upcoming_events.append(reg)
		else:
			past_events.append(reg)

	# Sort by date
	context.upcoming_events = sorted(upcoming_events, key=lambda x: str(x.event_date or ""), reverse=False)
	context.past_events = sorted(past_events, key=lambda x: str(x.event_date or ""), reverse=True)
