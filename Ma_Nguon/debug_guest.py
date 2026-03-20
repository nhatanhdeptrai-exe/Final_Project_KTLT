import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from repositories.guest_repository import GuestRepository
repo = GuestRepository()
gs = repo.get_all()
for g in gs:
    print(f"g.id={g.id} name={g.full_name} email={g.email} phone={g.phone} user_id={g.user_id}")

print(f"\nTotal guests: {len(gs)}")

# Check contracts
from handlers.xml_handler import XMLHandler
contracts = XMLHandler.get_all('data/xml/contracts.xml', 'contracts')
for c in contracts:
    print(f"contract id={c.get('id')} guest_id={c.get('guest_id')} room_id={c.get('room_id')} status={c.get('status')}")
