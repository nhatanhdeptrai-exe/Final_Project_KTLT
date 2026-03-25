"""
IoT Simulator — Giả lập ESP32 gửi chỉ số điện/nước qua MQTT.

Chạy riêng: py iot_simulator.py
Sẽ publish dữ liệu mỗi 5 giây cho tất cả phòng (đọc từ rooms.json).
"""
import json
import time
import random
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

# ── Config ──
BROKER = 'broker.hivemq.com'
PORT = 1883
TOPIC_PREFIX = 'phongtro_ktlt'
ROOMS_FILE = Path(__file__).parent / 'data' / 'json' / 'rooms.json'

# Chỉ số tích lũy
initial_readings = {}


def load_rooms():
    """Đọc danh sách phòng từ rooms.json (tự cập nhật khi thêm phòng)."""
    try:
        with open(ROOMS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [r['room_number'] for r in data.get('rooms', [])]
    except Exception:
        return ['P101', 'P102', 'P103']


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"✅ Connected to MQTT broker: {BROKER}")
    print(f"📡 Publishing to: {TOPIC_PREFIX}/#")
    print("=" * 50)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    print(f"🔌 Connecting to {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    try:
        while True:
            # Đọc lại rooms.json mỗi vòng → tự cập nhật phòng mới
            rooms = load_rooms()

            for room in rooms:
                # Khởi tạo chỉ số ban đầu nếu phòng mới
                if room not in initial_readings:
                    initial_readings[room] = {
                        'electric': round(random.uniform(100, 500), 1),
                        'water': round(random.uniform(10, 80), 1),
                    }

                # Tăng chỉ số realistic
                initial_readings[room]['electric'] += round(random.uniform(0.1, 0.5), 2)
                initial_readings[room]['electric'] = round(initial_readings[room]['electric'], 2)
                initial_readings[room]['water'] += round(random.uniform(0.01, 0.05), 3)
                initial_readings[room]['water'] = round(initial_readings[room]['water'], 3)

                now = datetime.now().isoformat()

                # Publish electric
                client.publish(f"{TOPIC_PREFIX}/{room}/electric", json.dumps({
                    'room': room, 'type': 'electric',
                    'value': initial_readings[room]['electric'],
                    'unit': 'kWh', 'timestamp': now,
                }))

                # Publish water
                client.publish(f"{TOPIC_PREFIX}/{room}/water", json.dumps({
                    'room': room, 'type': 'water',
                    'value': initial_readings[room]['water'],
                    'unit': 'm³', 'timestamp': now,
                }))

            # Log
            ts = datetime.now().strftime('%H:%M:%S')
            sample = rooms[0] if rooms else '?'
            e = initial_readings.get(sample, {}).get('electric', 0)
            w = initial_readings.get(sample, {}).get('water', 0)
            print(f"[{ts}] 📊 {len(rooms)} phòng | {sample}: ⚡{e} kWh, 💧{w} m³")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
