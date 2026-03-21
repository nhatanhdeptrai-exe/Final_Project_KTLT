import py_compile
import sys

files = [
    'ui/UI_Admin/views/account_management_view.py',
    'ui/UI_Admin/views/guest_management_view.py',
    'ui/UI_Admin/views/invoice_management_view.py',
    'ui/UI_Admin/views/room_management_view.py',
    'ui/UI_Admin/views/repair_management_view.py',
    'ui/UI_Common/views/auth_window.py',
    'ui/UI_Guest/views/guest_account_view.py',
    'ui/UI_Guest/views/my_room_view.py',
    'ui/UI_Guest/views/dang_ky_phong_view.py',
    'ui/UI_Common/custom_popup.py',
]

ok = 0
err = 0
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        ok += 1
        print(f"OK: {f}")
    except Exception as e:
        err += 1
        print(f"ERR: {f} -> {e}")

print(f"\nTotal OK: {ok}, ERR: {err}")
