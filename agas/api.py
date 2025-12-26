import frappe
import secrets
import string
from frappe.utils import validate_email_address, now_datetime
from datetime import timedelta

# Rate limiting settings
OTP_EXPIRY = 300  # 5 minutes
MAX_OTP_REQUESTS = 3  # Max requests per hour per identifier
RATE_LIMIT_WINDOW = 3600  # 1 hour

@frappe.whitelist(allow_guest=True)
def send_otp(email_or_mobile):
	"""
	Generates and sends a 6-digit OTP to the provided email or mobile.
	"""
	if not email_or_mobile:
		frappe.throw("Email or Mobile Number is required", frappe.ValidationError)

	# Validate if it's an email (simplistic check for mobile for now)
	is_email = False
	if "@" in email_or_mobile:
		if not validate_email_address(email_or_mobile):
			frappe.throw("Invalid Email Address", frappe.ValidationError)
		is_email = True

	# Rate Limiting Check
	rate_limit_key = f"otp_request_limit_{email_or_mobile}"
	request_count = frappe.cache().get_value(rate_limit_key) or 0
	
	if request_count >= MAX_OTP_REQUESTS:
		frappe.throw("Too many OTP requests. Please try again later.", frappe.RateLimitExceededError)

	# Generate 6-digit secure OTP
	otp = ''.join(secrets.choice(string.digits) for _ in range(6))
	
	# Store in cache
	cache_key = f"otp_verify_{email_or_mobile}"
	frappe.cache().set_value(cache_key, otp, expires_in_sec=OTP_EXPIRY)

	# Update rate limit
	frappe.cache().set_value(rate_limit_key, request_count + 1, expires_in_sec=RATE_LIMIT_WINDOW)

	# Send OTP
	if is_email:
		send_otp_via_email(email_or_mobile, otp)
	else:
		# Placeholder for SMS logic
		# send_otp_via_sms(email_or_mobile, otp)
		# For now, we log it so it can be seen in tests/logs if SMS isn't configured
		frappe.log_error(f"OTP for {email_or_mobile}: {otp}", "OTP Send (Mobile)")
		# If user requested mobile but we only support email for now:
		# frappe.throw("SMS gateway not configured. Please use email.")

	return {"message": "OTP sent successfully"}

def send_otp_via_email(email, otp):
	subject = "Your Verification Code"
	message = f"""
	<div style="font-family: sans-serif; padding: 20px;">
		<h2>Verification Code</h2>
		<p>Your one-time password (OTP) is: <strong style="font-size: 24px; color: #1a73e8;">{otp}</strong></p>
		<p>This code is valid for 5 minutes. Do not share it with anyone.</p>
		<hr>
		<p style="font-size: 12px; color: #777;">If you did not request this code, please ignore this email.</p>
	</div>
	"""
	try:
		frappe.sendmail(
			recipients=email,
			subject=subject,
			message=message,
			now=True
		)
	except Exception as e:
		# Log the error but don't crash.
		frappe.log_error(title="OTP Email Error", message=f"Failed to send to {email}: {str(e)}")
		# For DEV environment, we will log the OTP to console so developer can see it
		print(f"DEV OTP for {email}: {otp}")

@frappe.whitelist(allow_guest=True)
def verify_otp_and_login(email_or_mobile, otp, set_password=None):
	"""
	Verifies OTP. Logs in the user if successful. Creates a new user if not exists.
	Optionally sets a password for future logins.
	"""
	if not email_or_mobile or not otp:
		frappe.throw("Email/Mobile and OTP are required", frappe.ValidationError)

	cache_key = f"otp_verify_{email_or_mobile}"
	cached_otp = frappe.cache().get_value(cache_key)

	if not cached_otp:
		frappe.throw("OTP expired or not requested. Please request a new one.", frappe.AuthenticationError)

	if cached_otp != otp:
		frappe.throw("Invalid OTP", frappe.AuthenticationError)

	# OTP Verified - Clear it
	frappe.cache().delete_value(cache_key)

	# Check User
	user_id = email_or_mobile
	# Resolve the true User ID from Member Profile if necessary
	if not frappe.db.exists("User", user_id):
		resolved_user = frappe.db.get_value("Member Profile", {"email_id": email_or_mobile}, "user") or \
						frappe.db.get_value("Member Profile", {"mobile_no": email_or_mobile}, "user")
		if resolved_user:
			user_id = resolved_user
	
	user_exists = frappe.db.exists("User", user_id)
	
	if not user_exists:
		# Create User (Signup)
		user = frappe.get_doc({
			"doctype": "User",
			"email": user_id if "@" in user_id else f"{user_id}@example.com", # Fallback for mobile
			"first_name": "Visitor",
			"enabled": 1,
			"user_type": "Website User"
		})
		user.flags.no_welcome_mail = True
		user.insert(ignore_permissions=True)
		
		# Assign baseline roles if they exist
		for role in ["Website User", "Guest"]:
			if frappe.db.exists("Role", role):
				user.add_roles(role)
				break
		
		# Set password if provided
		if set_password:
			user.new_password = set_password
			user.save(ignore_permissions=True)
		
		frappe.db.commit()
	else:
		# Existing user - update password if provided
		if set_password:
			user = frappe.get_doc("User", user_id)
			user.new_password = set_password
			user.save(ignore_permissions=True)
			frappe.db.commit()

	# Login
	frappe.local.login_manager = frappe.auth.LoginManager()
	frappe.local.login_manager.user = user_id
	frappe.local.login_manager.post_login()
	
	return {
		"message": "Logged in successfully",
		"home_page": "/member_profile",
		"password_set": bool(set_password)
	}

@frappe.whitelist()
def change_password(new_password):
	"""
	Changes the password for the currently logged-in user.
	Follows Frappe's internal password complexity norms.
	"""
	if not new_password:
		frappe.throw("New password is required", frappe.ValidationError)
	
	user_id = frappe.session.user
	if user_id == "Guest":
		frappe.throw("Not logged in", frappe.PermissionError)

	try:
		user = frappe.get_doc("User", user_id)
		user.new_password = new_password
		user.save(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		# Extract message if it's a Frappe exception
		msg = str(e)
		if hasattr(e, 'message'):
			msg = e.message
		frappe.throw(msg)

	return {"message": "Password updated successfully"}

@frappe.whitelist(allow_guest=True)
def login_with_password(identifier, password):
	"""
	Login with email or mobile number and password for returning users.
	"""
	if not identifier or not password:
		frappe.throw("Email/Mobile and password are required", frappe.ValidationError)
	
	# Resolve the true User ID
	user_id = identifier
	if not frappe.db.exists("User", identifier):
		# Check Member Profile for email or mobile
		resolved_user = frappe.db.get_value("Member Profile", 
			{"email_id": identifier}, "user") or \
			frappe.db.get_value("Member Profile", 
			{"mobile_no": identifier}, "user")
		
		if resolved_user:
			user_id = resolved_user

	try:
		# Use Frappe's built-in authentication
		frappe.local.login_manager = frappe.auth.LoginManager()
		frappe.local.login_manager.authenticate(user_id, password)
		frappe.local.login_manager.post_login()
		
		return {
			"message": "Logged in successfully",
			"home_page": "/member_profile"
		}
	except frappe.AuthenticationError:
		frappe.throw("Invalid email/mobile or password", frappe.AuthenticationError)

@frappe.whitelist(allow_guest=True)
def submit_contact_form(name, email, message):
	"""
	Handles contact form submission. Sends an email to the admin.
	"""
	if not name or not email or not message:
		frappe.throw("All fields are required", frappe.ValidationError)

	if not validate_email_address(email):
		frappe.throw("Invalid Email Address", frappe.ValidationError)

	# 1. Store in a Note or dedicated DocType (Optional, using simple logging/email for now)
	# For better tracking, one might create a 'Contact Inquiry' DocType.
	
	# 2. Send Email to Admin (Mocking the admin email for now)
	admin_email = "admin@agasashram.org" 
	subject = f"New Contact Inquiry from {name}"
	email_message = f"""
	<div style="font-family: sans-serif; padding: 20px;">
		<h3>New Inquiry Received</h3>
		<p><strong>Name:</strong> {name}</p>
		<p><strong>Email:</strong> {email}</p>
		<p><strong>Message:</strong></p>
		<blockquote style="background: #f9f9f9; padding: 15px; border-left: 4px solid #5d4037;">
			{message}
		</blockquote>
	</div>
	"""
	
	try:
		frappe.sendmail(
			recipients=admin_email,
			subject=subject,
			message=email_message,
			reply_to=email,
			now=True
		)
	except Exception as e:
		frappe.log_error(title="Contact Form Email Error", message=f"Failed to send email: {str(e)}")
		# Don't throw error to user if logging fails, but maybe return a warning
	
	return {"message": "Thank you! Your message has been sent."}

@frappe.whitelist()
def get_member_profile():
	"""
	Returns the Member Profile for the current user.
	"""
	user = frappe.session.user
	if user == "Guest":
		return None
	
	profile = frappe.db.get_value("Member Profile", {"user": user}, "*", as_dict=True)
	if not profile:
		# Create a dummy or empty structure to help frontend
		profile = {
			"first_name": "",
			"middle_name": "",
			"last_name": "",
			"gender": "",
			"email_id": user,
			"user": user
		}
	return profile

@frappe.whitelist()
def save_member_profile(data):
	"""
	Saves or updates the Member Profile for the current user.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login to save your profile", frappe.PermissionError)

	if isinstance(data, str):
		data = frappe.parse_json(data)

	# Validate unique mobile number
	mobile_no = data.get("mobile_no")
	if mobile_no:
		profile_name = frappe.db.get_value("Member Profile", {"user": user}, "name")
		existing_profile = frappe.db.get_value("Member Profile", 
			{"mobile_no": mobile_no, "name": ["!=", profile_name or ""]}, "name")
		if existing_profile:
			frappe.throw("This mobile number is already registered with another user", frappe.ValidationError)

	profile_name = frappe.db.get_value("Member Profile", {"user": user}, "name")
	
	if profile_name:
		doc = frappe.get_doc("Member Profile", profile_name)
		frappe.logger().info(f"Updating Member Profile {profile_name} with keys: {list(data.keys())}")
		for key, value in data.items():
			if key not in ["name", "doctype", "user"]:
				doc.set(key, value)
		doc.save(ignore_permissions=True)
	else:
		data["doctype"] = "Member Profile"
		data["user"] = user
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
	
	# Sync with User record
	try:
		user_doc = frappe.get_doc("User", user)
		user_updated = False
		
		# Map Member Profile fields to User fields
		mapping = {
			"first_name": "first_name",
			"last_name": "last_name",
			"gender": "gender",
			"mobile_no": "mobile_no",
			"date_of_birth": "birth_date",
			"photo": "user_image"
		}
		
		for member_key, user_key in mapping.items():
			if member_key in data:
				val = data.get(member_key)
				if user_doc.get(user_key) != val:
					user_doc.set(user_key, val)
					user_updated = True
		
		if user_updated:
			user_doc.save(ignore_permissions=True)
			
	except Exception as e:
		frappe.logger().error(f"Error syncing User record for {user}: {str(e)}")

	frappe.db.commit()
	return {"message": "Profile saved successfully", "name": doc.name}

@frappe.whitelist()
def register_for_event(data):
	"""
	Creates or updates an Event Registration record.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login to register for events", frappe.PermissionError)

	if isinstance(data, str):
		data = frappe.parse_json(data)

	# Validate email format
	email = data.get("email")
	if email and not validate_email_address(email):
		frappe.throw("Invalid email address format", frappe.ValidationError)

	event_title = data.get("event")
	if not event_title:
		frappe.throw("Event is required")

	# Validate visitor members - check if visiting members have visit dates
	if "visitor_members" in data and isinstance(data["visitor_members"], list):
		for member in data["visitor_members"]:
			if member.get("is_visiting") == 1 and not member.get("visit_date"):
				member_name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
				frappe.throw(f"Visit date is required for {member_name or 'visiting member'}", frappe.ValidationError)

	# Validate food requirements
	if data.get("food_required") == "Yes":
		food_schedule = data.get("food_schedule", [])
		has_meals = False
		for day in food_schedule:
			if day.get("breakfast") or day.get("lunch") or day.get("dinner"):
				has_meals = True
				break
		if not has_meals:
			frappe.throw("Please select at least one meal if food is required.", frappe.ValidationError)

	# Check for existing registration for this user and event
	existing_name = frappe.db.get_value("Event Registration", 
		{"user": user, "event": event_title}, "name")

	finalize = data.get("finalize", False)
	data["doctype"] = "Event Registration"
	data["user"] = user
	
	if existing_name:
		doc = frappe.get_doc("Event Registration", existing_name)
		# Update fields except some system ones
		for key, value in data.items():
			if key not in ["name", "doctype", "user", "visitor_members", "food_schedule", "finalize"]:
				doc.set(key, value)
		
		# If previously Draft and now finalizing, move to Registered
		if finalize:
			doc.status = "Registered"
		elif not doc.status:
			doc.status = "Draft"

		# Handle child table: Replace all if provided
		if "visitor_members" in data:
			doc.set("visitor_members", [])
			for member in data["visitor_members"]:
				member["doctype"] = "Event Registration Member"
				doc.append("visitor_members", member)

		if "food_schedule" in data:
			doc.set("food_schedule", [])
			for day in data["food_schedule"]:
				day["doctype"] = "Event Food Day"
				doc.append("food_schedule", day)
		
		doc.save(ignore_permissions=True)
	else:
		data["status"] = "Registered" if finalize else "Draft"
		if "visitor_members" in data:
			for member in data["visitor_members"]:
				member["doctype"] = "Event Registration Member"
		
		if "food_schedule" in data:
			for day in data["food_schedule"]:
				day["doctype"] = "Event Food Day"
		
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
	
	frappe.db.commit()
	msg = "Registration successful" if finalize else "Progress saved as Draft"
	return {"message": msg, "name": doc.name, "status": doc.status}

@frappe.whitelist()
def get_family_members():
	"""
	Returns a list of family members for the current member profile.
	"""
	user = frappe.session.user
	if user == "Guest":
		return []
	
	profile_name = frappe.db.get_value("Member Profile", {"user": user}, "name")
	if not profile_name:
		return []
	
	return frappe.get_all("Family Member", 
		filters={"primary_member": profile_name},
		fields=["*"],
		order_by="creation asc"
	)

@frappe.whitelist()
def save_family_member(data):
	"""
	Creates or updates a Family Member record.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login to manage family members", frappe.PermissionError)

	if isinstance(data, str):
		data = frappe.parse_json(data)

	profile_name = frappe.db.get_value("Member Profile", {"user": user}, "name")
	if not profile_name:
		frappe.throw("Please create your member profile first")

	adultchild = data.get("adultchild")
	contact_no = data.get("contact_no")
	primary_mobile = frappe.db.get_value("Member Profile", profile_name, "mobile_no")

	if adultchild == "Adult" and not contact_no:
		frappe.throw("Contact number is required for adult family members", frappe.ValidationError)

	# Validate unique mobile number for family members
	if contact_no:
		allow_primary = adultchild in ["Child", "Senior Citizen"] and contact_no == primary_mobile
		if not allow_primary:
			existing_family = frappe.db.get_value("Family Member", 
				{"contact_no": contact_no, "name": ["!=", data.get("name") or ""]}, "name")
			if existing_family:
				frappe.throw("This mobile number is already registered with another family member", frappe.ValidationError)
			
			# Also check against primary member profiles (excluding self)
			existing_profile = frappe.db.get_value("Member Profile", 
				{"mobile_no": contact_no, "name": ["!=", profile_name]}, "name")
			if existing_profile:
				frappe.throw("This mobile number is already registered with another user", frappe.ValidationError)

	data["doctype"] = "Family Member"
	data["primary_member"] = profile_name

	# Explicit check for mandatory files
	if not data.get("photo"):
		frappe.throw("Photo is required", frappe.ValidationError)
	if not data.get("id_proof"):
		frappe.throw("ID Proof Document is required", frappe.ValidationError)

	if data.get("name"):
		doc = frappe.get_doc("Family Member", data["name"])
		# Check ownership
		if doc.primary_member != profile_name:
			frappe.throw("Not authorized to edit this record", frappe.PermissionError)
		
		frappe.logger().info(f"Updating Family Member {data.get('name')} with keys: {list(data.keys())}")
		for key, value in data.items():
			if key not in ["name", "doctype", "primary_member"]:
				doc.set(key, value)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
	
	frappe.db.commit()
	return {"message": "Family member saved successfully", "name": doc.name}

@frappe.whitelist()
def delete_family_member(name):
	"""
	Deletes a Family Member record.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login", frappe.PermissionError)

	profile_name = frappe.db.get_value("Member Profile", {"user": user}, "name")
	doc = frappe.get_doc("Family Member", name)
	
	if doc.primary_member != profile_name:
		frappe.throw("Not authorized", frappe.PermissionError)
	
	doc.delete()
	frappe.db.commit()
	return {"message": "Deleted successfully"}

@frappe.whitelist()
def cancel_registration(registration_name, reason=None):
	"""
	Cancels an Event Registration.
	"""
	user = frappe.session.user
	if user == "Guest":
		frappe.throw("Please login", frappe.PermissionError)

	if not reason:
		frappe.throw("Cancellation reason is required", frappe.ValidationError)
	
	doc = frappe.get_doc("Event Registration", registration_name)
	if doc.user != user:
		frappe.throw("Not authorized", frappe.PermissionError)
	
	doc.status = "Cancelled"
	doc.cancellation_reason = reason
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return "Registration cancelled successfully"
