import os
os.environ.setdefault("SECRET_KEY", "test-secret")
from app import app
from database.session import SessionLocal, create_database
from models.user import User
from models.document import Document
from services.persistence_service import persistence_service

create_database()
db = SessionLocal()
try:
    user = db.query(User).first()
    if user:
        stats = persistence_service.dashboard_stats(user.id)
        assert "planning_count" in stats
        print("PERSISTENCE SMOKE OK", stats)
    else:
        print("PERSISTENCE SMOKE OK - no user rows")
finally:
    db.close()

client = app.test_client()
assert client.get("/health").status_code == 200
assert client.get("/planning/").status_code == 302
assert client.get("/curriculum/").status_code == 302
assert client.get("/evaluation/").status_code == 302
print("ROUTE SMOKE OK")
