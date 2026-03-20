"""UserRepository."""
from typing import Optional, List
from config.constants import USERS_FILE
from handlers.json_handler import JSONHandler
from models.user import User

class UserRepository:
    def __init__(self):
        self.file_path = USERS_FILE
        self.list_key = 'users'

    def get_by_id(self, user_id: int) -> Optional[User]:
        data = JSONHandler.find_by_id(self.file_path, user_id, self.list_key)
        return User.from_dict(data) if data else None

    def get_all(self) -> List[User]:
        return [User.from_dict(item) for item in JSONHandler.get_all(self.file_path, self.list_key)]

    def create(self, user: User) -> User:
        user_data = user.to_dict()
        user_data.pop('id', None)
        saved = JSONHandler.add_item(self.file_path, user_data, self.list_key)
        return User.from_dict(saved)

    def update(self, user: User) -> bool:
        if not user.id: return False
        updates = user.to_dict()
        updates.pop('id', None)
        return JSONHandler.update_item(self.file_path, user.id, updates, self.list_key)

    def delete(self, user_id: int) -> bool:
        return JSONHandler.delete_item(self.file_path, user_id, self.list_key)

    def get_by_email(self, email: str) -> Optional[User]:
        for data in JSONHandler.get_all(self.file_path, self.list_key):
            if data.get('email', '').lower() == email.lower(): return User.from_dict(data)
        return None

    def get_by_phone(self, phone: str) -> Optional[User]:
        for data in JSONHandler.get_all(self.file_path, self.list_key):
            if data.get('phone') == phone: return User.from_dict(data)
        return None

    def authenticate(self, login: str, password: str) -> Optional[User]:
        user = self.get_by_email(login) or self.get_by_phone(login)
        if user and user.check_password(password): return user
        return None
