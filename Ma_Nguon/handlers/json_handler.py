"""
JSONHandler - Đọc/ghi dữ liệu JSON.
"""
import json
import os
from typing import Dict, List, Optional

class JSONHandler:
    @staticmethod
    def _ensure_file(file_path: str, default_data: Dict = None) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data or {}, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(file_path: str) -> Dict:
        JSONHandler._ensure_file(file_path, {})
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def save(file_path: str, data: Dict) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add_item(file_path: str, item: Dict, list_key: str = 'items') -> Dict:
        data = JSONHandler.load(file_path)
        if list_key not in data: data[list_key] = []
        if 'last_id' not in data: data['last_id'] = 0
        data['last_id'] += 1
        item['id'] = data['last_id']
        data[list_key].append(item)
        JSONHandler.save(file_path, data)
        return item

    @staticmethod
    def update_item(file_path: str, item_id: int, updates: Dict, list_key: str = 'items') -> bool:
        data = JSONHandler.load(file_path)
        items = data.get(list_key, [])
        for item in items:
            if item.get('id') == item_id:
                item.update(updates)
                JSONHandler.save(file_path, data)
                return True
        return False

    @staticmethod
    def delete_item(file_path: str, item_id: int, list_key: str = 'items') -> bool:
        data = JSONHandler.load(file_path)
        items = data.get(list_key, [])
        for i, item in enumerate(items):
            if item.get('id') == item_id:
                items.pop(i)
                JSONHandler.save(file_path, data)
                return True
        return False

    @staticmethod
    def find_by_id(file_path: str, item_id: int, list_key: str = 'items') -> Optional[Dict]:
        data = JSONHandler.load(file_path)
        for item in data.get(list_key, []):
            if item.get('id') == item_id: return item
        return None

    @staticmethod
    def get_all(file_path: str, list_key: str = 'items') -> List[Dict]:
        return JSONHandler.load(file_path).get(list_key, [])
