"""ApplicationRepository — CRUD đơn đăng ký thuê. Storage: XML (rental_applications.xml)"""
from typing import Optional, List
from config.constants import APPLICATIONS_FILE
from handlers.xml_handler import XMLHandler
from models.application import Application


class ApplicationRepository:
    def __init__(self):
        self.file_path = APPLICATIONS_FILE
        self.root_tag = 'rental_applications'
        self.item_tag = 'application'

    def get_by_id(self, app_id: int) -> Optional[Application]:
        data = XMLHandler.find_by_id(self.file_path, app_id, self.root_tag)
        return Application.from_dict(data) if data else None

    def get_all(self) -> List[Application]:
        return [Application.from_dict(d) for d in XMLHandler.get_all(self.file_path, self.root_tag)]

    def create(self, app: Application) -> Application:
        d = app.to_dict()
        d.pop('id', None)
        saved = XMLHandler.add_item(self.file_path, d, self.root_tag, self.item_tag)
        return Application.from_dict(saved)

    def update(self, app: Application) -> bool:
        if not app.id: return False
        d = app.to_dict()
        d.pop('id', None)
        return XMLHandler.update_item(self.file_path, app.id, d, self.root_tag)

    def delete(self, app_id: int) -> bool:
        return XMLHandler.delete_item(self.file_path, app_id, self.root_tag)

    def get_by_guest_id(self, guest_id: int) -> List[Application]:
        return [a for a in self.get_all() if a.guest_id == guest_id]
