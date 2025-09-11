from sqlalchemy.sql import Executable
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

def get_raw_sql(query: Executable, engine: Engine | AsyncEngine) -> str:
    """
    Compile SQLAlchemy query menjadi raw SQL string dengan literal values.
    
    :param query: SQLAlchemy query object (select, insert, update, dll.)
    :param engine: SQLAlchemy Engine atau AsyncEngine
    :return: string raw SQL
    """
    # Ambil dialect yang benar
    dialect = (
        engine.sync_engine.dialect if isinstance(engine, AsyncEngine) else engine.dialect
    )

    compiled = query.compile(
        dialect=dialect,
        compile_kwargs={"literal_binds": True}
    )
    return str(compiled)

from typing import Type, Any
from pydantic import BaseModel

from typing import Type, Union, Sequence
from pydantic import BaseModel

def map_to_pydantic(
    result: Union[Sequence, object, None], 
    schema: Type[BaseModel]
) -> Union[list[BaseModel], BaseModel, None]:
    """
    Konversi hasil SQLAlchemy execute (ORM object / Row / list) 
    menjadi Pydantic model atau list of models.
    
    - Bisa handle single row atau list
    - Bisa handle ORM object atau Row (partial select)
    """

    if result is None:
        return None

    # Kalau input berupa list / sequence
    if isinstance(result, (list, tuple, set)):
        models = []
        for row in result:
            if hasattr(row, "__table__"):  
                # ORM object
                models.append(schema.model_validate(row, from_attributes=True))
            else:
                # Row atau tuple dari partial select
                models.append(schema.model_validate(dict(row._mapping)))
        return models

    # Kalau single ORM object
    if hasattr(result, "__table__"):
        return schema.model_validate(result, from_attributes=True)

    # Kalau single Row
    if hasattr(result, "_mapping"):
        return schema.model_validate(dict(result._mapping))

    raise ValueError(f"Unsupported result type: {type(result)}")
