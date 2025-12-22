import frappe

def run():
	logs = frappe.get_all('Error Log', fields=['method', 'error'], limit=5, order_by='creation desc')
	for log in logs:
		print(f"--- {log.method} ---")
		print(log.error[:500])
