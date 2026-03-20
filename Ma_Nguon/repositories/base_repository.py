"""BaseRepository — Lớp cơ sở cho tất cả repository."""
from typing import Optional, List, Dict


class BaseRepository:
    """Abstract base class cho các repository."""
    def get_by_id(self, item_id: int):
        raise NotImplementedError

    def get_all(self) -> list:
        raise NotImplementedError

    def create(self, item):
        raise NotImplementedError

    def update(self, item) -> bool:
        raise NotImplementedError

    def delete(self, item_id: int) -> bool:
        raise NotImplementedError
