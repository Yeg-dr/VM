import time

class RelayController:
    """
    RelayController is responsible for simulating relay-based item dispensing.

    This class abstracts the process of controlling relays used to dispense
    products in a vending machine. It relies on an external lookup function
    to fetch item details based on item codes.
    """

    def __init__(self, item_lookup_func):
        """
        Initialize the relay controller.

        Args:
            item_lookup_func (callable): A function that accepts an item code (str)
                                         and returns item information (dict).
        """
        self.item_lookup_func = item_lookup_func

    def dispense(self, selected_items, status_callback):
        """
        Simulate dispensing items by activating relays.

        Args:
            selected_items (list of dict): A list of dictionaries representing items
                                           selected by the user. Each dict must include:
                                           - code (str): The item code.
                                           - name (str): The item name.
            status_callback (callable): A callback function to update the UI or logs
                                        with status messages. Receives a single str argument.

        Behavior:
            - Displays a starting message.
            - Iterates over each selected item and simulates relay activation.
            - If an item code cannot be found, reports an error via the callback.
            - Reports completion at the end of the dispensing process.
        """
        # Notify that dispensing has started
        status_callback("Starting dispensing process...")
        time.sleep(1)
        
        for item in selected_items:
            info = self.item_lookup_func(item["code"])
            if info:
                location = info.get("location", "Unknown")
                status_callback(f"Dispensing: {item['name']} from {location}...")
                
                # Simulate relay activation (placeholder for actual hardware control)
                print(f"Activating relay for location {location} (item: {item['name']})")
                time.sleep(2)  # Simulated delay for relay action
            else:
                status_callback(f"Error: Item code {item['code']} not found!")
                time.sleep(1)

        # Notify that dispensing has completed
        status_callback("Dispensing completed successfully")
