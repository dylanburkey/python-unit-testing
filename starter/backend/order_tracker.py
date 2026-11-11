# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        """
        Creates a new order and persists it to storage.

        Raises:
            ValueError: if an order with the same ID already exists.

        Returns:
            The newly created order as a dict.
        """
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)
        return order

    def get_order_by_id(self, order_id: str):
        """
        Returns the order with the given ID, or None if it does not exist.
        """
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        """
        Changes the status of an existing order and persists the change.

        Raises:
            ValueError: if no order with the given ID exists.

        Returns:
            The updated order as a dict.
        """
        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' not found.")

        order["status"] = new_status
        self.storage.save_order(order_id, order)
        return order

    def list_all_orders(self):
        """
        Returns a list of all orders currently in storage.
        """
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        """
        Returns a list of orders whose status matches the given status.
        """
        return [
            order for order in self.storage.get_all_orders().values()
            if order.get("status") == status
        ]
