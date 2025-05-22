from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

AcademicWritingSchema = declarative_base(metadata=MetaData(schema="academic_writing_schema"))
