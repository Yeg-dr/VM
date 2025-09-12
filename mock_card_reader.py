import random
import time

class CardReader:
    def __init__(self):
        """
        Simulated card reader for handling test payments.
        """
        pass

    def charge(self, amount):
        """
        Simulate a payment transaction.

        Args:
            amount (float): The amount to be charged.

        Returns:
            dict: A dictionary containing transaction details:
                - success (bool): Whether the payment was successful.
                - message (str): Status message.
                - amount (float): The charged amount.
                - transaction_id (str, optional): Unique ID for successful transactions.
                - error_code (str, optional): Error code for failed transactions.

        Notes:
            - Simulates a delay of 2 seconds to mimic real-world processing.
            - Randomly determines success or failure of the transaction.
        """
        # Simulate real-world payment delay
        time.sleep(2)
        
        # Randomly determine if payment succeeds or fails
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
