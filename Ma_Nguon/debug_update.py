"""Debug: Test guest update for concakpvp"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repositories.guest_repository import GuestRepository
from services.guest_service import GuestService

repo = GuestRepository()
svc = GuestService(repo)

guest = svc.get_guest_by_user_id(3)
if guest:
    print(f"Found guest: id={guest.id}, name={guest.full_name}")
    print(f"  gender={guest.gender!r}, dob={guest.dob!r}, id_card={guest.id_card!r}")
    
    guest.gender = "Nam"
    guest.dob = "15/6/1995"
    guest.id_card = "012345678901"
    ok, msg = svc.update_guest(guest)
    print(f"  Update ok={ok}")
    
    guest2 = svc.get_guest_by_user_id(3)
    print(f"  After reload: gender={guest2.gender!r}, dob={guest2.dob!r}, id_card={guest2.id_card!r}")
else:
    print("No guest for user_id=3")
    for g in svc.get_all_guests():
        print(f"  id={g.id} uid={g.user_id} name={g.full_name}")
