"""IoTService — Giả lập đọc số điện nước từ IoT Module."""
import random
from typing import Dict, List
from repositories.room_repository import RoomRepository


class IoTService:
    def __init__(self, room_repo: RoomRepository):
        self.room_repo = room_repo

    def read_electricity(self, room_id: int) -> int:
        """Giả lập đọc số điện (kWh)."""
        return random.randint(50, 300)

    def read_water(self, room_id: int) -> float:
        """Giả lập đọc số nước (m³)."""
        return round(random.uniform(3.0, 15.0), 1)

    def read_all_meters(self) -> Dict[int, Dict]:
        """Đọc số điện nước tất cả phòng đang thuê."""
        rooms = self.room_repo.get_all()
        result = {}
        for room in rooms:
            if room.status == 'occupied':
                result[room.id] = {
                    'electricity_kwh': self.read_electricity(room.id),
                    'water_m3': self.read_water(room.id),
                }
        return result

    def calculate_costs(self, electricity_rate: int = 3500, water_rate: int = 25000) -> Dict[int, Dict]:
        """Tính chi phí điện nước cho tất cả phòng."""
        meters = self.read_all_meters()
        costs = {}
        for room_id, data in meters.items():
            elec_cost = data['electricity_kwh'] * electricity_rate
            water_cost = int(data['water_m3'] * water_rate)
            costs[room_id] = {
                'electricity_cost': elec_cost,
                'water_cost': water_cost,
                'electricity_kwh': data['electricity_kwh'],
                'water_m3': data['water_m3'],
            }
        return costs
