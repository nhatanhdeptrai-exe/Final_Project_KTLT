"""Script to create test guest account: tk=22, mk=22, renting room 'qưe' (id=12)"""
import sys
sys.path.insert(0, '.')

import bcrypt
import json
from datetime import datetime

# 1. Add user to users.json (skip if already exists)
users_file = 'data/json/users.json'
with open(users_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

existing = [u for u in data["users"] if u["email"] == "22"]
if existing:
    new_user = existing[0]
    print(f"User already exists id={new_user['id']}")
else:
    pw_hash = bcrypt.hashpw('22'.encode(), bcrypt.gensalt()).decode()
    new_user = {
        "email": "22",
        "phone": "22",
        "password_hash": pw_hash,
        "full_name": "Guest Test 22",
        "role": "guest",
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "id": data["last_id"] + 1
    }
    data["users"].append(new_user)
    data["last_id"] = new_user["id"]
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Created user id={new_user['id']}")

# 2. Add guest record to guests.xlsx
from repositories.guest_repository import GuestRepository
from models.guest import Guest

guest_repo = GuestRepository()
new_guest = Guest(
    user_id=new_user["id"],
    full_name="Guest Test 22",
    id_card="123456789012",
    phone="22",
    email="22",
    address="Test address",
    occupation="Test",
)
saved_guest = guest_repo.create(new_guest)
print(f"Created guest id={saved_guest.id}")

# 3. Update room status to occupied
rooms_file = 'data/json/rooms.json'
with open(rooms_file, 'r', encoding='utf-8') as f:
    rdata = json.load(f)

for room in rdata["rooms"]:
    if room["id"] == 12:
        room["status"] = "occupied"
        room["updated_at"] = datetime.now().isoformat()
        print(f"Room id={room['id']} -> occupied")
        break

with open(rooms_file, 'w', encoding='utf-8') as f:
    json.dump(rdata, f, ensure_ascii=False, indent=2)

# 4. Create active contract
from handlers.xml_handler import XMLHandler

contract_data = {
    'contract_number': f'HD{datetime.now().strftime("%Y%m")}008',
    'room_id': '12',
    'guest_id': str(saved_guest.id),
    'start_date': '2026-03-01',
    'end_date': '2027-02-28',
    'monthly_rent': '12313',
    'deposit': '12313',
    'status': 'active',
    'created_at': datetime.now().isoformat(),
    'updated_at': datetime.now().isoformat(),
}
saved = XMLHandler.add_item('data/xml/contracts.xml', contract_data, 'contracts', 'contract')
print(f"Created contract id={saved.get('id')}")

print("\n✅ Done! Account: tk=22, mk=22, renting room 'qưe'")
