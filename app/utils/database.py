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
    - Otomatis mengecualikan field yang di-exclude di schema
    """

    if result is None:
        return None

    # Kalau input berupa list / sequence
    if isinstance(result, (list, tuple, set)):
        models = []
        for row in result:
            if hasattr(row, "__table__"):  
                # ORM object - buat dict tanpa field yang di-exclude
                excluded_fields = _get_excluded_fields(schema)
                row_dict = _convert_orm_to_dict(row, excluded_fields)
                models.append(schema.model_validate(row_dict))
            else:
                # Row atau tuple dari partial select
                models.append(schema.model_validate(dict(row._mapping)))
        return models

    # Kalau single ORM object
    if hasattr(result, "__table__"):
        excluded_fields = _get_excluded_fields(schema)
        row_dict = _convert_orm_to_dict(result, excluded_fields)
        return schema.model_validate(row_dict)

    # Kalau single Row
    if hasattr(result, "_mapping"):
        return schema.model_validate(dict(result._mapping))

    raise ValueError(f"Unsupported result type: {type(result)}")

def _get_excluded_fields(schema: Type[BaseModel]) -> set[str]:
    """
    Mendapatkan field yang di-exclude dari schema Pydantic.
    """
    excluded_fields = set()
    
    # Periksa field annotations untuk field dengan exclude=True
    for field_name, field_info in schema.model_fields.items():
        if hasattr(field_info, 'exclude') and field_info.exclude:
            excluded_fields.add(field_name)
    
    return excluded_fields

def _convert_orm_to_dict(orm_obj, excluded_fields: set[str]) -> dict:
    """
    Konversi ORM object ke dictionary, mengecualikan field yang di-exclude.
    """
    result_dict = {}
    
    # Iterasi melalui semua attribute dari ORM object
    for attr_name in dir(orm_obj):
        # Skip private attributes dan method
        if attr_name.startswith('_'):
            continue
        
        # Skip jika field di-exclude
        if attr_name in excluded_fields:
            continue
            
        # Dapatkan nilai attribute
        try:
            value = getattr(orm_obj, attr_name)
            # Skip jika itu adalah method atau callable
            if callable(value):
                continue
            result_dict[attr_name] = value
        except AttributeError:
            continue
    
    return result_dict
