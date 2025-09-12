"""
relay_controller.py
-------------------
ماژول کنترل رله‌ها برای دستگاه وندینگ ماشین
--------------------------------------------
این ماژول به صورت مستقیم با GPIO های Raspberry Pi کار می‌کند و وظیفه‌ی فعال‌سازی
رله‌ها بر اساس لوکیشن تعریف‌شده در فایل آیتم‌ها (vending_items.json) را دارد.

لوکیشن‌ها در فایل JSON به صورت ترکیب «حرف + عدد» هستند (مثل A1, C3, H4).
- حروف (A تا H) نشان‌دهنده‌ی ردیف‌ها (۸ ردیف).
- اعداد (1 تا 4) نشان‌دهنده‌ی ستون‌ها (۴ ستون).

بنابراین یک ماتریس ۸×۴ تشکیل می‌شود (۳۲ آیتم در کل).
این کلاس لوکیشن را به اندیس عددی تبدیل می‌کند و سپس GPIO متناظر را فعال می‌نماید.
"""

import RPi.GPIO as GPIO
import time


class RelayMatrix:
    """
    کلاس سطح پایین برای کنترل ماتریس رله‌ها.

    این کلاس تنها وظیفه‌ی فعال‌سازی یک ردیف و ستون مشخص را دارد.
    """

    def __init__(self, row_pins, col_pins, pulse_time=0.5):
        """
        پارامترها:
            row_pins: لیست پین‌های GPIO مربوط به ردیف‌ها (A تا H)
            col_pins: لیست پین‌های GPIO مربوط به ستون‌ها (۱ تا ۴)
            pulse_time: مدت زمان فعال بودن رله (بر حسب ثانیه)
        """
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.pulse_time = pulse_time

        # آماده‌سازی GPIO
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
        فعال‌سازی یک رله بر اساس شماره‌ی ردیف و ستون.

        پارامترها:
            row: شماره ردیف (۰ تا ۷)
            col: شماره ستون (۰ تا ۳)
            status_callback: تابعی برای ارسال پیام وضعیت به UI
        """
        if not (0 <= row < len(self.row_pins)) or not (0 <= col < len(self.col_pins)):
            raise ValueError("ردیف یا ستون خارج از محدوده است")

        self._reset()
        GPIO.output(self.row_pins[row], GPIO.HIGH)
        GPIO.output(self.col_pins[col], GPIO.HIGH)

        if status_callback:
            status_callback(f"⏳ در حال آزادسازی: ردیف {row}, ستون {col}")

        time.sleep(self.pulse_time)
        self._reset()

    def activate_by_index(self, index, status_callback=None):
        """
        فعال‌سازی بر اساس اندیس عددی (۰ تا ۳۱).

        فرمول محاسبه:
            index = row_index * تعداد ستون‌ها + col_index
        """
        total_items = len(self.row_pins) * len(self.col_pins)
        if not (0 <= index < total_items):
            raise ValueError("شماره آیتم خارج از محدوده است (۰ تا ۳۱)")

        row = index // len(self.col_pins)
        col = index % len(self.col_pins)
        self.activate(row, col, status_callback)

    def cleanup(self):
        """آزادسازی پین‌های GPIO"""
        GPIO.cleanup()


class RelayController:
    """
    کنترلر سطح بالا برای وندینگ ماشین.
    وظیفه دارد لیست آیتم‌ها را گرفته و رله‌ی مربوط به هر آیتم را فعال کند.
    """

    def __init__(self, item_lookup):
        """
        پارامترها:
            item_lookup: تابعی که با دریافت کد آیتم، اطلاعات آیتم را برمی‌گرداند.
        """
        self.item_lookup = item_lookup

        # پین‌های GPIO (باید بر اساس سیم‌کشی واقعی تنظیم شوند)
        self.row_pins = [17, 27, 22, 23, 24, 25, 8, 7]   # ردیف‌های A تا H
        self.col_pins = [5, 6, 13, 19]                   # ستون‌های 1 تا 4

        self.matrix = RelayMatrix(self.row_pins, self.col_pins, pulse_time=1)

    def location_to_index(self, location: str):
        """
        تبدیل لوکیشن (مثل 'C2') به اندیس عددی (۰ تا ۳۱).

        فرمول:
            row_index = A→0, B→1, ..., H→7
            col_index = (عدد - ۱) → ۰ تا ۳
            index = row_index * 4 + col_index
        """
        if not location or len(location) < 2:
            raise ValueError(f"Invalid location: {location}")

        row_letter = location[0].upper()
        col_number = int(location[1])  # 1 تا 4

        row_index = ord(row_letter) - ord('A')  # A=0 … H=7
        col_index = col_number - 1             # 1=0 … 4=3

        return row_index * len(self.col_pins) + col_index

    def dispense(self, selected_items, status_callback=None):
        """
        آزادسازی یک لیست از آیتم‌ها.

        پارامترها:
            selected_items: لیست آیتم‌ها (هر آیتم شامل location است)
            status_callback: تابعی برای ارسال وضعیت به UI
        """
        for item in selected_items:
            loc = item.get("location")
            if not loc:
                if status_callback:
                    status_callback(f"⚠️ آیتم {item['code']} فاقد اطلاعات مکان است")
                continue

            try:
                index = self.location_to_index(loc)
                self.matrix.activate_by_index(index, status_callback)
                if status_callback:
                    status_callback(f"✅ آیتم {item['name']} با موفقیت آزاد شد")
                time.sleep(0.5)  # فاصله‌ی کوتاه بین آیتم‌ها
            except Exception as e:
                if status_callback:
                    status_callback(f"❌ خطا در آزادسازی {item['name']}: {e}")

        self.matrix.cleanup()
