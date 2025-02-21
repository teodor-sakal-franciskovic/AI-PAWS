from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

BaseSchema = declarative_base(metadata=MetaData(schema="base_schema"))
