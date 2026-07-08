"""AulaMind base platform schema for fresh databases."""
from alembic import op
from database.base import Base

# Register model metadata.
from models.school import School
from models.subscription import Subscription
from models.user import User
from models.course import Course
from models.subject import Subject
from models.unit import Unit
from models.learning_objective import LearningObjective

revision = "20260708_00"
down_revision = None
branch_labels = None
depends_on = None

BASE_TABLES = [
    "schools", "subscriptions", "users", "courses", "subjects", "units", "learning_objectives"
]

def upgrade():
    bind = op.get_bind()
    tables = [Base.metadata.tables[name] for name in BASE_TABLES]
    Base.metadata.create_all(bind=bind, tables=tables, checkfirst=True)

def downgrade():
    bind = op.get_bind()
    for name in reversed(BASE_TABLES):
        Base.metadata.tables[name].drop(bind=bind, checkfirst=True)
