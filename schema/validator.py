from jsonschema import Draft7Validator
from .schema import SCHEMA
from .spatial_logic import validate_spatial_integrity
from config.standards import MIN_ROOM_AREAS
from typing import Dict, Any


def check_standards(data: Dict[str, Any]):
    """Check if rooms meet minimum area standards."""
    errors = []
    for i, r in enumerate(data.get('rooms', [])):
        r_type = r.get('type')
        area = float(r['width']) * float(r['height'])
        min_area = MIN_ROOM_AREAS.get(r_type, 0)
        if area < min_area:
            name = r.get('name', f"Room {i}")
            errors.append(f"{name} area ({area:.1f}m2) is below standard ({min_area}m2).")
    if errors:
        raise ValueError("\n".join(errors))


def _fill_defaults(schema, instance):
    """Helper to fill default values from JSON schema."""
    if 'default' in schema and (instance is None):
        return schema['default']
    if schema.get('type') == 'object':
        inst = instance or {}
        for prop, subschema in schema.get('properties', {}).items():
            if prop not in inst and 'default' in subschema:
                inst[prop] = subschema['default']
            elif prop in inst:
                inst[prop] = _fill_defaults(subschema, inst[prop])
        return inst
    if schema.get('type') == 'array':
        if instance is None:
            return schema.get('default', [])
        itemschema = schema.get('items')
        return [_fill_defaults(itemschema, it) for it in instance]
    return instance


def validate_and_fill(data: Dict[str, Any]) -> Dict[str, Any]:
    '''Validate incoming dict against schema and fill defaults.'''
    validator = Draft7Validator(SCHEMA)
    
    filled = _fill_defaults(SCHEMA, data)
    
    # Standard JSON Schema Validation
    errors = sorted(validator.iter_errors(filled), key=lambda e: e.path)
    if errors:
        msgs = '; '.join([f"{'/'.join(map(str,e.path))}: {e.message}" for e in errors])
        raise ValueError(f"Schema errors: {msgs}")
    
    # Advanced Architectural Validation
    validate_spatial_integrity(filled)
    check_standards(filled)
    
    return filled
