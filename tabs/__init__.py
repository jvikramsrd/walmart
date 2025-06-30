# This file makes the tabs directory a Python package
from tabs import orders, inventory, delivery, warehouse, optimizer

TABS = {
    "Orders": {
        "func": orders.app,
        "icon": "box-seam"
    },
    "Inventory": {
        "func": inventory.app,
        "icon": "bookshelf"
    },
    "Delivery": {
        "func": delivery.app,
        "icon": "truck"
    },
    "Warehouse": {
        "func": warehouse.app,
        "icon": "building"
    },
    "Optimizer": {
        "func": optimizer.app,
        "icon": "graph-up-arrow"
    }
}
