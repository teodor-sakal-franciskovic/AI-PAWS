from logging.config import fileConfig

from alembic import context
from app.database.config import DATABASE_URL
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
from app.main import AcademicWritingSchema  # noqa
from app.models.assignment import Assignment  # noqa
from app.models.assignment_rule_group import AssignmentRuleGroup  # noqa
from app.models.course import Course  # noqa
from app.models.course_group import CourseGroup  # noqa
from app.models.course_instructor import CourseInstructor  # noqa
from app.models.course_submission_language import CourseSubmissionLanguage  # noqa
from app.models.feedback import Feedback  # noqa
from app.models.fulfillment import Fulfillment  # noqa
from app.models.group import Group  # noqa
from app.models.historical_profile import HistoricalProfile  # noqa
from app.models.language import Language  # noqa
from app.models.prompt_template import PromptTemplate  # noqa
from app.models.role import Role  # noqa
from app.models.rule import Rule  # noqa
from app.models.rule_feedback_submission import RuleFeedbackSubmission  # noqa
from app.models.rule_group import RuleGroup  # noqa
from app.models.submission import Submission  # noqa
from app.models.submission_mode import SubmissionMode  # noqa
from app.models.user import User  # noqa
from app.models.user_course_points import UserCoursePoints  # noqa

# target_metadata = mymodel.Base.metadata
target_metadata = [
    AcademicWritingSchema.metadata,
]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

LIST_OF_SCHEMAS_TO_BE_SCANNED = ["public", "academic_writing_schema"]


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in LIST_OF_SCHEMAS_TO_BE_SCANNED
    else:
        return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
            include_name=include_name,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
