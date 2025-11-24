
# Tambahkan helper function jika diperlukan
import inspect
from sqlalchemy.inspection import inspect as sa_inspect
from fastapi.routing import APIRoute
from pydantic import BaseModel
import shortuuid
from fastapi import Request
from passlib.hash import bcrypt
import bcrypt as _bcrypt

from app.core.context import generate_tx_id, reset_route, reset_tx_id, set_route, set_tx_id
from typing import Any, Iterable

def is_awaitable(obj):
    return inspect.isawaitable(obj) or hasattr(obj, "__await__") or inspect.iscoroutinefunction(obj)

def hash_password(password: str) -> str:
    try:
        return bcrypt.hash(password)
    except Exception as e:
        print(f"Error during password hashing: {e}")
        print(f"Using bcrypt library")
        try:
            return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
        except Exception as e:
            print(f"Error during password hashing: {e}")
            return None

def verify_password(plain_password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    Prefers passlib.hash.bcrypt.verify if available, otherwise uses bcrypt.checkpw.
    """
    try:
        return bcrypt.verify(plain_password, hashed)
    except Exception as e:
        print(f"Error during password verification: {e}")
        print(f"Using bcrypt library")
        try:
            return _bcrypt.checkpw(plain_password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            print(f"Error during password verification: {e}")
            # If neither library is available, return False
            return False

def get_current_route(request: Request) -> dict:
    """
    Ambil informasi route & method dari Request.
    """
    return {
        "full_url": str(request.url),
        "path": request.scope.get("path"),
        "method": request.method,
        "endpoint": request.scope.get("endpoint").__name__ if request.scope.get("endpoint") else None,
        "route_name": request.scope.get("route").name if request.scope.get("route") else None,
    }

def get_route_tags(request: Request) -> list[str]:
    """Dependency to get the tags of the current route."""
    route = None
    for r in request.app.routes:
        if isinstance(r, APIRoute) and r.path_regex.match(request.scope["path"]):
            route = r
            break
    
    if route and hasattr(route, "tags"):
        return route.tags
    return []

def get_route_name(request: Request) -> str:
    """
    Dependency to get the name of the current route.
    Matches both path and HTTP method for accurate route identification.
    """
    route = None
    request_method = request.method
    request_path = request.scope["path"]
    
    for r in request.app.routes:
        if isinstance(r, APIRoute):
            # Check if path matches
            if r.path_regex.match(request_path):
                # Check if method matches (case-insensitive)
                if request_method.upper() in [method.upper() for method in r.methods]:
                    route = r
                    break
    
    # print(f"get_route_name: {route} (method: {request_method}, path: {request_path})")
    if route and hasattr(route, "name"):
        return route.name
    return None

async def init_route(request: Request, user: str, parent_act: str, act: str) -> tuple[str, dict, str, str]:
    tx_id = generate_tx_id(act=act)
    route = get_current_route(request)
    print(f"init_route: {act} {tx_id} {parent_act} {user} {route['path']}")
    setattr(request.state, "user", user)
    setattr(request.state, "tx_id", tx_id)
    setattr(request.state, "act", parent_act)
    tx_token = set_tx_id(tx_id)
    route_token = set_route(route['path'])
    setattr(request.state, "route", route['path'])
    return tx_id, route, tx_token, route_token

def end_route(tx_token: str, route_token: str) -> None:
    reset_tx_id(tx_token)
    reset_route(route_token)

def convert_pydantic_list_to_tuple(
    pydantic_list: list, 
    exclude_fields: list[str] | None = None,
    sort_fields: bool = False
) -> tuple[dict[str, int], list[list]]:
    """
    Convert a list of Pydantic models to a tuple containing field mapping and data rows.
    
    Args:
        pydantic_list (list): List of Pydantic model instances
        exclude_fields (list[str] | None): Optional list of field names to exclude from output.
                                          These fields will be removed from both field mapping and data rows.
        sort_fields (bool): If True, field names will be sorted alphabetically in ascending order.
                           Default is False (maintains original field order).
        
    Returns:
        tuple[dict[str, int], list[list]]: 
            - First element: Dictionary mapping field names to their column indices
            - Second element: List of data rows, where each row is a list of values
            
    Example:
        >>> users = [User(username='staff', email='staff@mail.com', is_active=True, password='secret')]
        >>> field_map, data_rows = convert_pydantic_list_to_tuple(users, exclude_fields=['password'])
        >>> field_map
        {'username': 0, 'email': 1, 'is_active': 2, ...}
        >>> data_rows
        [['staff', 'staff@mail.com', True, ...]]
        
        >>> # With field sorting
        >>> field_map, data_rows = convert_pydantic_list_to_tuple(users, sort_fields=True)
        >>> field_map
        {'email': 0, 'is_active': 1, 'password': 2, 'username': 3, ...}
        
        >>> # Without exclusions
        >>> field_map, data_rows = convert_pydantic_list_to_tuple(users)
        >>> field_map
        {'username': 0, 'email': 1, 'is_active': 2, 'password': 3, ...}
    """
    if not pydantic_list:
        return {}, []
    
    # Get field names from the first Pydantic model using model_dump() to respect exclusions
    first_model = pydantic_list[0]
    model_dict = first_model.model_dump()
    field_names = list(model_dict.keys())
    
    # Apply additional exclusions if provided
    if exclude_fields:
        field_names = [field for field in field_names if field not in exclude_fields]
    
    # Sort field names alphabetically if requested
    if sort_fields:
        field_names = sorted(field_names)
    
    # Create field mapping dictionary {field_name: index}
    field_mapping = {field_name: index for index, field_name in enumerate(field_names)}
    
    # Convert each Pydantic model to a list of values
    data_rows = []
    for model in pydantic_list:
        model_dict = model.model_dump()
        row = []
        for field_name in field_names:
            value = model_dict[field_name]
            # Convert datetime objects to strings for better serialization
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            row.append(value)
        data_rows.append(row)
    
    return field_mapping, data_rows

def extend_example(base_model: type[BaseModel], extra_example: dict) -> dict:
    """
    Extend jsmodel_config.get("json_schema_extra", {}).get("example", {})s:
        base_model: The Pydantic model class to extend
        extra_example: Additional example data to merge
        
    Returns:
        dict: Updated json_schema_extra configuration
        
    Example:
        >>> class MyModel(BaseModel):
        ...     name: str
        ...     age: int
        >>> 
        >>> extra = {"name": "John", "age": 30}
        >>> config = extend_example(MyModel, extra)
        >>> # Use in model_config: ConfigDict(json_schema_extra=config)
    """
    # Get existing json_schema_extra or create empty dict
    json_schema_extra = getattr(base_model.model_config, "json_schema_extra", {})
    
    # Get existing example or create empty dict
    base_example = json_schema_extra.get("example", {})
    
    # Merge base example with extra example
    merged_example = {**base_example, **extra_example}
    
    return {
        "example": merged_example
    }


def model_to_dict(obj: Any, exclude: Iterable[str] | None = None) -> dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to a dictionary.

    Args:
        obj (Any): SQLAlchemy model instance.
        exclude (Iterable[str] | None): Optional iterable of column names to
            exclude from the output dictionary.

    Returns:
        dict[str, Any]: Mapping of column name to value for the given model
        instance, excluding any columns specified in "exclude".
    """
    excluded_columns = set(exclude) if exclude else set()
    return {
        c.key: getattr(obj, c.key)
        for c in sa_inspect(obj).mapper.column_attrs
        if c.key not in excluded_columns
    }