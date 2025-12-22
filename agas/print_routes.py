import frappe
from frappe.website.router import get_pages

def run():
	pages = get_pages()
	# Just print the source of 'home'
	res = pages.get('home')
	print(f"HOME_PAGE_SOURCE: {res}")
