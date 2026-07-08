from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from config import Config
from database.base import Base

from models.user import User
from models.school import School
from models.subscription import Subscription
from models.course import Course
from models.subject import Subject
from models.unit import Unit
from models.learning_objective import LearningObjective
from models.document import Document
from models.ai_generation import AIGeneration
from models.export import Export
from models.usage_event import UsageEvent

config = context.config
config.set_main_option("sqlalchemy.url", Config.SQLALCHEMY_DATABASE_URI.replace("%", "%%"))
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
