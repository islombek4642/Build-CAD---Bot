from jsonschema import Draft7Validator
from .schema import SCHEMA
from typing import Dict, Any


def validate_and_fill(data: Dict[str, Any]) -> Dict[str, Any]:
    '''Validate incoming dict against schema and fill defaults.'''
    validator = Draft7Validator(SCHEMA)
    # Fill defaults
    def set_defaults(schema, instance):
        if 'default' in schema and (instance is None):
            return schema['default']
        if schema.get('type') == 'object':
            inst = instance or {}
            for prop, subschema in schema.get('properties', {}).items():
                if prop not in inst and 'default' in subschema:
                    inst[prop] = subschema['default']
                elif prop in inst:
                    inst[prop] = set_defaults(subschema, inst[prop])
            return inst
        if schema.get('type') == 'array':
            if instance is None:
                return schema.get('default', [])
            itemschema = schema.get('items')
            return [set_defaults(itemschema, it) for it in instance]
        return instance

    filled = set_defaults(SCHEMA, data)
    # Final validation (will raise if invalid)
    errors = sorted(validator.iter_errors(filled), key=lambda e: e.path)
    if errors:
        msgs = '; '.join([f"{'/'.join(map(str,e.path))}: {e.message}" for e in errors])
        raise ValueError(f"Schema validation errors: {msgs}")
    return filled
