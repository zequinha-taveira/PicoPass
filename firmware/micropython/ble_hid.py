# firmware/micropython/ble_hid.py
import bluetooth
import struct
from micropython import const

# --- BLE Constants ---
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# --- HID Service & Characteristics ---
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)
_REPORT_UUID = bluetooth.UUID(0x2A4D)
_REPORT_MAP_UUID = bluetooth.UUID(0x2A4B)
_HID_INFO_UUID = bluetooth.UUID(0x2A4A)
_HID_CONTROL_POINT_UUID = bluetooth.UUID(0x2A4C)

# HID Report Map (Standard Keyboard)
_REPORT_MAP = b'\x05\x01\x09\x06\xa1\x01\x85\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x01\x95\x06\x75\x08\x15\x00\x25d\x05\x07\x19\x00\x29d\x81\x00\xc0'

class BLEKeyboard:
    def __init__(self, name="PicoPass-Pro"):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        
        # Define HID Service
        self._handle_report, self._handle_report_map = self._register_services()
        
        self._conn_handle = None
        self._payload = self._advertising_payload(name=name, appearance=const(0x03C1))
        self._advertise()

    def _register_services(self):
        # HID Service Definition
        HID_SERV = (
            _HID_SERVICE_UUID,
            (
                (_REPORT_MAP_UUID, bluetooth.FLAG_READ),
                (_REPORT_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY, ( (bluetooth.UUID(0x2908), bluetooth.FLAG_READ, b'\x01\x01'), )), # Input Report
                (_HID_INFO_UUID, bluetooth.FLAG_READ, b'\x01\x11\x00\x02'), # bcdHID, bCountryCode, Flags
                (_HID_CONTROL_POINT_UUID, bluetooth.FLAG_WRITE_NO_RESPONSE),
            ),
        )
        handles = self._ble.gatts_register_services((HID_SERV,))
        # Return Report Input and Report Map handles
        return handles[0][1], handles[0][0]

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self._conn_handle, _, _ = data
            print("BLE Connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self._conn_handle = None
            print("BLE Disconnected")
            self._advertise()

    def _advertise(self, interval_us=100000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def _advertising_payload(self, name=None, appearance=0):
        payload = bytearray()
        def _append(adv_type, value):
            nonlocal payload
            payload.append(len(value) + 1)
            payload.append(adv_type)
            payload += value
        _append(const(0x01), struct.pack("B", 0x06))
        if name: _append(const(0x09), name.encode())
        if appearance: _append(const(0x19), struct.pack("<H", appearance))
        return payload

    def is_connected(self):
        return self._conn_handle is not None

    def send_report(self, modifier, keycodes):
        if not self.is_connected(): return
        # HID Keyboard Report: [Modifier, Reserved, Key1, Key2, Key3, Key4, Key5, Key6]
        report = bytearray(8)
        report[0] = modifier
        for i, code in enumerate(keycodes[:6]):
            report[i+2] = code
        self._ble.gatts_notify(self._conn_handle, self._handle_report, report)

    def type_text(self, text):
        if not self.is_connected(): return
        # Simple char to HID mapping (basic subset)
        mapping = {
            'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09, 'g': 0x0a, 'h': 0x0b, 
            'i': 0x0c, 'j': 0x0d, 'k': 0x0e, 'l': 0x0f, 'm': 0x10, 'n': 0x11, 'o': 0x12, 'p': 0x13,
            'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17, 'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b,
            'y': 0x1c, 'z': 0x1d, '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21, '5': 0x22, '6': 0x23,
            '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27, '\n': 0x28, ' ': 0x2c, '-': 0x2d, '=': 0x2e
        }
        for char in text:
            code = mapping.get(char.lower(), 0)
            if code:
                mod = 0x02 if char.isupper() else 0
                self.send_report(mod, [code])
                import utime
                utime.sleep_ms(10)
                self.send_report(0, [])
                utime.sleep_ms(10)
