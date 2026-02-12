from typing import Any, Dict
from config import settings

SCHEMA = {
    'type': 'object',
    'properties': {
        'total_area': {'type': 'number', 'default': settings.DEFAULT_TOTAL_AREA},
        'land_width': {'type': 'number', 'default': 10.0},
        'land_height': {'type': 'number', 'default': 10.0},
        'floor_count': {'type': 'integer', 'default': settings.DEFAULT_FLOOR_COUNT},
        'rooms': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'type': {'type': 'string'},
                    'x': {'type': 'number'},
                    'y': {'type': 'number'},
                    'width': {'type': 'number'},
                    'height': {'type': 'number'},
                    'separate': {'type': 'boolean', 'default': False},
                    'openings': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string', 'enum': ['door', 'window']},
                                'wall': {'type': 'string', 'enum': ['north', 'south', 'east', 'west']},
                                'pos': {'type': 'number'}
                            },
                            'required': ['type', 'wall', 'pos']
                        },
                        'default': []
                    }
                },
                'required': ['type', 'x', 'y', 'width', 'height']
            },
            'default': []
        },
        'entrance': {'type': 'string', 'enum': ['north', 'south', 'east', 'west'], 'default': settings.DEFAULT_ENTRANCE},
        'style': {'type': 'string', 'enum': ['Modern', 'Classic'], 'default': 'Modern'},
        'walls_thickness': {'type': 'number', 'default': settings.DEFAULT_WALLS_THICKNESS},
        'notes': {'type': 'string'}
    },
    'required': ['land_width', 'land_height', 'rooms']
}
