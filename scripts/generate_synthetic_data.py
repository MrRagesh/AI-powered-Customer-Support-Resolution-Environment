"""Generate synthetic support tickets for testing."""
import json, random, uuid

TEMPLATES = [
    "I need a refund for my order #{order}.",
    "My account is locked and I cannot log in.",
    "The mobile app crashes immediately on launch.",
    "I was charged twice for my subscription.",
    "My package #{order} hasn't arrived after 14 days.",
    "I cannot access the API — getting 401 errors.",
    "Please cancel my subscription and refund this month.",
    "The dashboard is showing incorrect data for the past week.",
    "I need to update my billing information but the form errors.",
    "My two-factor authentication stopped working after a phone change.",
]

def generate(n: int = 50):
    tickets = []
    for _ in range(n):
        template = random.choice(TEMPLATES)
        text = template.replace("{order}", str(random.randint(10000, 99999)))
        tickets.append({"id": str(uuid.uuid4()), "text": text})
    return tickets

if __name__ == "__main__":
    tickets = generate(50)
    with open("synthetic_tickets.json", "w") as f:
        json.dump(tickets, f, indent=2)
    print(f"Generated {len(tickets)} synthetic tickets → synthetic_tickets.json")
