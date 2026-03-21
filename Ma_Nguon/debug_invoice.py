import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Documents\Do_AN\Ma_Nguon')
from config.container import ServiceContainer

c = ServiceContainer()
ok, msg = c.auth_service.register('33', '33', '33', 'guest')
print(f'Register: ok={ok}, msg={msg}')

# Verify
user = c.auth_service.login('33', '33')
print(f'Login test: user={user}')
if user:
    print(f'  id={user.id}, name={user.full_name}, role={user.role}')
