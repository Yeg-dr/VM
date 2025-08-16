# relay_controller.py

import time

class RelayController:
    """
    Handles relay control for dispensing items.
    """

    def __init__(self, item_lookup_func):
        """
        Args:
            item_lookup_func (callable): Function to get item info by code.
        """
        self.item_lookup_func = item_lookup_func

    def dispense(self, selected_items, status_callback):
        """
        Simulate dispensing items via relays.

        Args:
            selected_items (list): List of item dicts as selected by user (order preserved).
            status_callback (callable): Function to update status messages. Receives a single str argument.
        """
        for item in selected_items:
            info = self.item_lookup_func(item["code"])
            location = info.get("location", None)
            status_callback(f"Dispensing item: {item['name']}...")
            # Simulate relay activation (replace with real hardware call later)
            print(f"Activating relay for location {location} (item: {item['name']})")
            time.sleep(1)  # mock delay for effect

        status_callback("All items were successfully dispensed")