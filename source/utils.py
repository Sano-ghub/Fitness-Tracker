def to_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.upper() == "TRUE"
    return bool(val)