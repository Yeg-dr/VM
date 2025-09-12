"""
ماژول کنترل واقعی رله‌ها برای دستگاه وندینگ ماشین
-------------------------------------------------
این ماژول جایگزین mock_relay_controller می‌شود و به صورت واقعی
GPIO های Raspberry Pi را برای آزادسازی آیتم‌ها کنترل می‌کند.
"""

import RPi.GPIO as GPIO
import time


class RelayMatrix:
    """
    کلاس سطح پایین برای کنترل مستقیم ماتریس رله‌ها.
    """

    def __init__(self, row_pins, col_pins, pulse_time=0.5):
        """
        پارامترها:
            row_pins: لیست پین‌های GPIO مربوط به ردیف‌ها (A تا H)
            col_pins: لیست پین‌های GPIO مربوط به ستون‌ها (1 تا 4)
            pulse_time: مدت زمان فعال بودن هر رله (بر حسب ثانیه)
        """
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.pulse_time = pulse_time

        # تنظیم GPIO ها
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.row_pins + self.col_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def _reset(self):
        """خاموش کردن همه‌ی ردیف‌ها و ستون‌ها"""
        for pin in self.row_pins + self.col_pins:
            GPIO.output(pin, GPIO.LOW)

    def activate(self, row, col, status_callback=None):
        """
        فعال‌سازی یک رله مشخص با توجه به شماره ردیف و ستون.
        """
        if not (0 <= row < len(self.row_pins)) or not (0 <= col < len(self.col_pins)):
            raise ValueError("Row or column index out of range")

        self._reset()
        GPIO.output(self.row_pins[row], GPIO.HIGH)
        GPIO.output(self.col_pins[col], GPIO.HIGH)

        if status_callback:
            status_callback(f"Dispensing from row {row}, col {col}...")

        time.sleep(self.pulse_time)
        self._reset()

    def activate_by_index(self, index, status_callback=None):
        """
        فعال‌سازی یک رله بر اساس اندیس عددی (0 تا 31).
        """
        total_items = len(self.row_pins) * len(self.col_pins)
        if not (0 <= index < total_items):
            raise ValueError("Item index out of range (0–31)")

        row = index // len(self.col_pins)
        col = index % len(self.col_pins)
        self.activate(row, col, status_callback)

    def cleanup(self):
        """آزادسازی منابع GPIO"""
        GPIO.cleanup()


class RelayController:
    """
    کنترلر سطح بالا برای آزادسازی آیتم‌ها در وندینگ ماشین.
    """

    def __init__(self, item_lookup_func):
        """
        پارامترها:
            item_lookup_func: تابعی برای دریافت اطلاعات آیتم بر اساس کد آن.
        """
        self.item_lookup_func = item_lookup_func

        # ⚠️ توجه: شماره پین‌ها باید متناسب با سیم‌کشی واقعی تغییر یابد
        self.row_pins = [17, 27, 22, 23, 24, 25, 8, 7]   # A تا H
        self.col_pins = [5, 6, 13, 19]                   # 1 تا 4

        self.matrix = RelayMatrix(self.row_pins, self.col_pins, pulse_time=1)

    def location_to_index(self, location: str):
        """
        تبدیل location مثل 'C2' به اندیس عددی (0 تا 31).
        """
        if not location or len(location) < 2:
            raise ValueError(f"Invalid location: {location}")

        row_letter = location[0].upper()
        col_number = int(location[1])  # ستون (1 تا 4)

        row_index = ord(row_letter) - ord('A')  # A=0 … H=7
        col_index = col_number - 1              # 1=0 … 4=3

        return row_index * len(self.col_pins) + col_index

    def dispense(self, selected_items, status_callback):
        """
        آزادسازی لیست آیتم‌ها.

        پارامترها:
            selected_items: لیستی از آیتم‌های انتخاب‌شده توسط کاربر
            status_callback: تابعی برای ارسال پیام وضعیت به UI
        """
        status_callback("Starting dispensing process...")
        time.sleep(1)

        for item in selected_items:
            info = self.item_lookup_func(item["code"])
            if not info:
                status_callback(f"Error: Item code {item['code']} not found!")
                continue

            loc = info.get("location")
            if not loc:
                status_callback(f"Error: Item {item['code']} has no location info")
                continue

            try:
                index = self.location_to_index(loc)
                self.matrix.activate_by_index(index, status_callback)
                status_callback(f"Dispensed: {item['name']} from {loc}")
                time.sleep(0.5)
            except Exception as e:
                status_callback(f"Error dispensing {item['name']}: {e}")

        self.matrix.cleanup()
        status_callback("Dispensing completed successfully")
