"""IoT Service — MQTT subscriber nhận chỉ số điện/nước realtime."""
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# File lưu chỉ số
IOT_DATA_FILE = Path(__file__).parent.parent / 'data' / 'json' / 'iot_readings.json'

# MQTT config
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = 'phongtro_ktlt'


class IoTService:
    """Service nhận dữ liệu IoT qua MQTT, lưu vào JSON."""

    def __init__(self):
        self._client = None
        self._running = False
        self._thread = None
        self._readings: Dict[str, dict] = {}
        self._load_data()

    def _load_data(self):
        """Load chỉ số đã lưu từ file."""
        if IOT_DATA_FILE.exists():
            try:
                with open(IOT_DATA_FILE, 'r', encoding='utf-8') as f:
                    self._readings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._readings = {}

    def _save_data(self):
        """Lưu chỉ số ra file."""
        IOT_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(IOT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._readings, f, ensure_ascii=False, indent=2)

    def get_latest(self, room_number: str) -> Optional[dict]:
        """Lấy chỉ số mới nhất của phòng."""
        return self._readings.get(room_number)

    def get_all_readings(self) -> Dict[str, dict]:
        """Lấy tất cả chỉ số."""
        return dict(self._readings)

    def start(self):
        """Bắt đầu subscribe MQTT."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._mqtt_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Dừng MQTT."""
        self._running = False
        if self._client:
            try:
                self._client.disconnect()
            except Exception:
                pass

    def _mqtt_loop(self):
        """Background thread chạy MQTT client."""
        try:
            import paho.mqtt.client as mqtt

            def on_connect(client, userdata, flags, reason_code, properties=None):
                topic = f"{MQTT_TOPIC_PREFIX}/#"
                client.subscribe(topic)
                print(f"[IoT] Connected to MQTT broker, subscribed: {topic}")

            def on_message(client, userdata, msg):
                try:
                    payload = json.loads(msg.payload.decode('utf-8'))
                    room = payload.get('room', '')
                    if not room:
                        return

                    if room not in self._readings:
                        self._readings[room] = {}

                    reading_type = payload.get('type', '')
                    self._readings[room][reading_type] = {
                        'value': payload.get('value', 0),
                        'unit': payload.get('unit', ''),
                        'timestamp': payload.get('timestamp', datetime.now().isoformat()),
                    }
                    self._readings[room]['last_update'] = datetime.now().isoformat()

                    self._save_data()
                except (json.JSONDecodeError, Exception) as e:
                    print(f"[IoT] Error processing message: {e}")

            def on_disconnect(client, userdata, flags, reason_code, properties=None):
                print(f"[IoT] Disconnected (rc={reason_code})")

            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.on_connect = on_connect
            client.on_message = on_message
            client.on_disconnect = on_disconnect
            self._client = client

            while self._running:
                try:
                    client.connect(MQTT_BROKER, MQTT_PORT, 60)
                    client.loop_forever()
                except Exception as e:
                    print(f"[IoT] Connection error: {e}")
                    if self._running:
                        time.sleep(5)

        except ImportError:
            print("[IoT] paho-mqtt not installed. Run: pip install paho-mqtt")
