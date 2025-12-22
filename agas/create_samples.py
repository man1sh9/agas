import frappe
from frappe.utils import add_days, nowdate

def run():
	events = [
		{
			"title": "Maha Shivratri Spiritual Night",
			"subtitle": "A night of divine connection",
			"event_date": add_days(nowdate(), 5),
			"event_time": "18:00:00",
			"venue": "Main Temple Hall",
			"published": 1,
			"description": "Join us for a powerful night of chanting, meditation, and rituals dedicated to Lord Shiva."
		},
		{
			"title": "Weekend Meditation Retreat",
			"subtitle": "Reset your mind and soul",
			"event_date": add_days(nowdate(), 15),
			"event_time": "06:00:00",
			"venue": "North Gardens",
			"published": 1,
			"description": "A 2-day immersive experience in silence and mindfulness techniques."
		},
		{
			"title": "Annual Satsang Meet",
			"subtitle": "Community Wisdom Sharing",
			"event_date": add_days(nowdate(), -10),
			"event_time": "10:00:00",
			"venue": "Satsang Bhavan",
			"published": 1,
			"description": "A look back at our growth and sharing wisdom for the upcoming year."
		}
	]

	for entry in events:
		if not frappe.db.exists("Agas Event", entry["title"]):
			doc = frappe.get_doc({
				"doctype": "Agas Event",
				**entry
			})
			doc.insert()
	
	frappe.db.commit()
	print("Sample events created!")
