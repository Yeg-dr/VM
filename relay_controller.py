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
        status_callback("Starting dispensing process...")
        time.sleep(1)
        
        for item in selected_items:
            info = self.item_lookup_func(item["code"])
            if info:
                location = info.get("location", "Unknown")
                status_callback(f"Dispensing: {item['name']} from {location}...")
                # Simulate relay activation (replace with real hardware call later)
                print(f"Activating relay for location {location} (item: {item['name']})")
                time.sleep(2)  # mock delay for effect
            else:
                status_callback(f"Error: Item code {item['code']} not found!")
                time.sleep(1)

        status_callback("Dispensing completed successfully")