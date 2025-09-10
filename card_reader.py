import random
import time

class CardReader:
    def __init__(self):
        pass

    def charge(self, amount):
        """
        شبیه‌سازی پرداخت تستی:
        - کمی تأخیر ایجاد می‌کند (2 ثانیه)
        - به صورت تصادفی موفق یا ناموفق برمی‌گرداند
        """
        time.sleep(2)  # شبیه‌سازی زمان واقعی پرداخت
        
        # انتخاب تصادفی موفق یا ناموفق بودن پرداخت
        success = random.choice([True, False])
        
        if success:
            return {
                "success": True, 
                "message": "Payment successful", 
                "amount": amount,
                "transaction_id": f"TXN{random.randint(10000, 99999)}"
            }
        else:
            return {
                "success": False, 
                "message": "Payment failed: Insufficient funds", 
                "amount": amount,
                "error_code": "INSUFFICIENT_FUNDS"
            }