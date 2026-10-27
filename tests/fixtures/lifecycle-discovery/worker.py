current_ids = []
namespace_id = None


def start(db):
    global namespace_id
    row = db.fetch_one("SELECT id FROM namespaces WHERE name = ?", ["preview"])
    namespace_id = row["id"] if row else db.execute_insert(
        "INSERT INTO namespaces (name) VALUES (?)", ["preview"]
    )


def process_item(db):
    item_id = db.execute_insert(
        "INSERT INTO items (namespace_id) VALUES (?)", [namespace_id]
    )
    current_ids.append(item_id)


def finish(db):
    for item_id in current_ids:
        db.execute("DELETE FROM items WHERE id = ?", [item_id])
    db.execute("DELETE FROM namespaces WHERE id = ?", [namespace_id])
