"""The three fictional scenarios used by the app and presentation handout."""

DEMO_TICKETS = {
    "Routine question": {
        "product": "Headphones", "ticket_type": "General inquiry",
        "subject": "Product question", "channel": "Email",
        "response_hours": 1.0, "previous_contacts": 0,
        "complaint_text": "I need help understanding the warranty on my headphones. A short explanation would be helpful. I can wait for a regular update.",
    },
    "Work disrupted": {
        "product": "Laptop", "ticket_type": "Technical issue",
        "subject": "Device not working", "channel": "Phone",
        "response_hours": 38.0, "previous_contacts": 4,
        "complaint_text": "My laptop keeps restarting. I cannot continue my work and need help urgently. Repeated attempts have failed and I need immediate assistance.",
    },
    "Repeated billing issue": {
        "product": "Phone", "ticket_type": "Billing inquiry",
        "subject": "Payment problem", "channel": "Chat",
        "response_hours": 22.0, "previous_contacts": 3,
        "complaint_text": "A payment appears twice and my payment has not been credited. I am frustrated that the problem is still unresolved. Please review the ticket history.",
    },
}
