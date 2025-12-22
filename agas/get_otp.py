import frappe

def run():
	email = "test_login@example.com"
	key = f"otp_verify_{email}"
	otp = frappe.cache().get_value(key)
	print(f"OTP for {email}: {otp}")
