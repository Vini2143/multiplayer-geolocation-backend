from sqlalchemy import String, Enum, cast

def query_builder(field, value):
    if isinstance(field.type, String):
        criteria = cast(field, String).ilike(f"%{value}%")
    else:
        criteria = field == value
    
    return criteria
