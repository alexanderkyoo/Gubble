import db
import sys

inventory_id = int(sys.argv[1])
rows = db.retrieveItems(inventory_id)

print(rows)