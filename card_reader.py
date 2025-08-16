# card_reader.py

class CardReader:
    """
    Simulates a card reader module.

    Usage:
        result = CardReader().charge(total_price)
        if result["success"]:
            # Payment successful
    """

    def charge(self, amount):
        """
        Simulate charging the provided amount to the card reader.

        Args:
            amount (float): The total price to charge.

        Returns:
            dict: {'success': True, 'message': 'Payment successful'}
        """
        # For now, always succeed (mock logic)
        return {
            "success": True,
            "message": "Payment successful"
        }