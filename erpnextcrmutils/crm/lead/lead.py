import frappe
from frappe import _
import re 
import erpnext.crm.utils
from erpnext.crm.doctype.lead.lead import Lead
import json




def address_exists(doc):
    """Check if an address linked to the document exists with the same details."""
    # Fetch linked addresses for the document
    linked_addresses = frappe.get_all("Dynamic Link", 
                                      filters={
                                          "link_doctype": doc.doctype, 
                                          "link_name": doc.name,
                                          "parenttype": "Address"
                                      }, 
                                      fields=["parent"])

    # Check each linked address for matching details
    for link in linked_addresses:
        # Using frappe.db.exists to check if an address with matching details exists
        if frappe.db.exists("Address", {
            "name": link.parent,
            "address_line1": doc.address_line1,
            "address_line2": doc.address_line2,
            "city": doc.city,
            "state": doc.state,
            "country": doc.country
        }):
            return True  # A matching linked address exists

    return False  # No matching linked address found



def on_update(doc, method=None):
    if frappe.get_single("CRM Settings").auto_creation_of_address and doc.get("address_line1") and doc.get("city") and doc.get("state"):
    # Check if a matching linked address exists
        if not address_exists(doc):
            # Create a new Address document since no match was found
            address = frappe.new_doc("Address")
            address.address_title = doc.name
            address.address_type = "Billing"  # Adjust as needed, e.g., "Shipping", "Billing"
            address.address_line1 = doc.address_line1
            address.address_line2 = doc.address_line2
            address.city = doc.city
            address.state = doc.state
            address.country = doc.country
            # Dynamically link the new address to the doc
            address.append('links', {
                'link_doctype': doc.doctype,
                'link_name': doc.name
            })
            address.insert()