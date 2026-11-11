import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#

# --- add_order ---

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()


def test_add_order_saves_correct_data(order_tracker, mock_storage):
    """Tests that the saved order contains the provided fields and default status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    })


def test_add_order_with_custom_status(order_tracker, mock_storage):
    """Tests that an explicit status overrides the 'pending' default."""
    order_tracker.add_order("ORD002", "Phone", 2, "CUST002", status="shipped")

    saved_order = mock_storage.save_order.call_args[0][1]
    assert saved_order["status"] == "shipped"


def test_add_order_returns_the_order(order_tracker, mock_storage):
    """Tests that add_order returns the newly created order."""
    result = order_tracker.add_order("ORD003", "Tablet", 3, "CUST003")

    assert result["order_id"] == "ORD003"
    assert result["status"] == "pending"


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

    mock_storage.save_order.assert_not_called()


# --- get_order_by_id ---

def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    """Tests fetching an existing order by its ID."""
    expected = {
        "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
        "customer_id": "CUST001", "status": "pending",
    }
    mock_storage.get_order.return_value = expected

    result = order_tracker.get_order_by_id("ORD001")

    mock_storage.get_order.assert_called_once_with("ORD001")
    assert result == expected


def test_get_order_by_id_returns_none_if_not_found(order_tracker, mock_storage):
    """Tests that fetching a non-existent order returns None."""
    mock_storage.get_order.return_value = None

    result = order_tracker.get_order_by_id("MISSING")

    mock_storage.get_order.assert_called_once_with("MISSING")
    assert result is None


# --- update_order_status ---

def test_update_order_status_changes_status(order_tracker, mock_storage):
    """Tests changing an order's status from 'pending' to 'shipped'."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
        "customer_id": "CUST001", "status": "pending",
    }

    result = order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.save_order.assert_called_once()
    saved_id, saved_order = mock_storage.save_order.call_args[0]
    assert saved_id == "ORD001"
    assert saved_order["status"] == "shipped"
    # Other fields must be preserved
    assert saved_order["item_name"] == "Laptop"
    assert saved_order["quantity"] == 1
    assert saved_order["customer_id"] == "CUST001"
    assert result["status"] == "shipped"


def test_update_order_status_raises_error_if_not_found(order_tracker, mock_storage):
    """Tests that updating a non-existent order raises a ValueError."""
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="Order with ID 'MISSING' not found."):
        order_tracker.update_order_status("MISSING", "shipped")

    mock_storage.save_order.assert_not_called()


# --- list_all_orders ---

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """Tests listing all current orders as a list."""
    order_a = {"order_id": "A", "item_name": "Item A", "quantity": 1, "customer_id": "C1", "status": "pending"}
    order_b = {"order_id": "B", "item_name": "Item B", "quantity": 2, "customer_id": "C2", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {"A": order_a, "B": order_b}

    result = order_tracker.list_all_orders()

    mock_storage.get_all_orders.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 2
    assert order_a in result
    assert order_b in result


def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    """Tests that listing orders with empty storage returns an empty list."""
    mock_storage.get_all_orders.return_value = {}

    result = order_tracker.list_all_orders()

    assert result == []


# --- list_orders_by_status ---

def test_list_orders_by_status_returns_only_matching_orders(order_tracker, mock_storage):
    """Tests retrieving only orders with a specific status."""
    pending = {"order_id": "A", "item_name": "Item A", "quantity": 1, "customer_id": "C1", "status": "pending"}
    shipped_1 = {"order_id": "B", "item_name": "Item B", "quantity": 2, "customer_id": "C2", "status": "shipped"}
    shipped_2 = {"order_id": "C", "item_name": "Item C", "quantity": 3, "customer_id": "C3", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {"A": pending, "B": shipped_1, "C": shipped_2}

    result = order_tracker.list_orders_by_status("shipped")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(order["status"] == "shipped" for order in result)
    assert pending not in result


def test_list_orders_by_status_returns_empty_list_when_no_match(order_tracker, mock_storage):
    """Tests that filtering by a status no order has returns an empty list."""
    mock_storage.get_all_orders.return_value = {
        "A": {"order_id": "A", "item_name": "Item A", "quantity": 1, "customer_id": "C1", "status": "pending"},
    }

    result = order_tracker.list_orders_by_status("delivered")

    assert result == []
