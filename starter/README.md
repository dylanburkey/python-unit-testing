# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## Reflection

- **Design decision.** `get_order_by_id` returns `None` for a missing order because an empty lookup is a normal result, while `update_order_status` raises a `ValueError` because mutating a nonexistent order is a caller mistake. The API maps `None` to 404 on GET and catches `ValueError` for 404 on PUT and 400 on duplicate POST, so the routes stay thin.
- **Trade-off.** Storage returns a dict keyed by ID, but the tracker's list methods return lists. The provided API tests index `response.json[0]`, so the reshaping has to live somewhere, and the tracker is the better home than the routes.
- **Testing insight.** `update_order_status` was the hardest test to mock because storage has no update method. Inspecting `save_order.call_args` to confirm the status changed and other fields survived drove the get-mutate-save implementation.
- **Next step.** Validate `quantity` as a positive integer and `status` against a known set. The API currently accepts `-1` and `"banana"` without complaint. A DELETE endpoint would follow.
