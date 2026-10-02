import os
import re

app_py_path = "/Users/elmehdinidazi/Downloads/Waiter/src/app.py"

# Replace route definition for kds_active
with open(app_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update kds_active route implementation
kds_route_old = """@app.route("/api/kds/active", methods=["GET"])
def kds_active():
    return jsonify(kds_service.get_active_kitchen_orders())"""

kds_route_new = """@app.route("/api/kds/active", methods=["GET"])
def kds_active():
    st = request.args.get("station")
    orders = kds_service.get_active_kitchen_orders(station=st)
    counts = kds_service.get_station_counts()
    return jsonify({
        "station": st or "ALL",
        "orders": orders,
        "station_counts": counts
    })"""

if kds_route_old in content:
    content = content.replace(kds_route_old, kds_route_new)
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("kds_active route updated successfully in app.py")
else:
    print("kds_route_old pattern not found or already updated.")
