import ezdxf
from ezdxf.entities import LWPolyline
from typing import Dict, Any, List, Tuple
from dxf_gen.components import room_rectangle
from config import settings


def _add_layer(doc, name: str, color: int = 7):
    if name not in doc.layers:
        doc.layers.new(name=name, dxfattribs={'color': color})


def create_plan(spec: Dict[str, Any], filename: str) -> str:
    # Create a realistic DXF floorplan based on the spec
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    _add_layer(doc, 'LAND', color=8)  # Gray for boundaries
    _add_layer(doc, 'WALLS', color=7)  # White/Black for walls
    _add_layer(doc, 'HATCH', color=253) # Light gray for fill
    _add_layer(doc, 'ROOM_LABELS', color=3) # Green for text
    _add_layer(doc, 'DIMENSIONS', color=1) # Red for dims
    _add_layer(doc, 'DOORS', color=4) # Cyan
    _add_layer(doc, 'WINDOWS', color=2) # Yellow

    land_w = float(spec.get('land_width', 10.0))
    land_h = float(spec.get('land_height', 10.0))
    wall_t = float(spec.get('walls_thickness', 0.3))

    # Draw Land Boundary
    land_pts = [(0, 0), (land_w, 0), (land_w, land_h), (0, land_h), (0, 0)]
    msp.add_lwpolyline(land_pts, dxfattribs={'layer': 'LAND', 'closed': True})

    # Draw Rooms with Walls
    rooms = spec.get('rooms', [])
    for r in rooms:
        x, y = float(r['x']), float(r['y'])
        w, h = float(r['width']), float(r['height'])
        name = r.get('name', r.get('type', 'room'))

        # Outer Wall
        outer_rect = room_rectangle((x, y), w, h)
        msp.add_lwpolyline(outer_rect, dxfattribs={'layer': 'WALLS', 'closed': True})

        # Inner Wall
        inner_rect = []
        if w > wall_t * 2 and h > wall_t * 2:
            inner_rect = room_rectangle((x + wall_t, y + wall_t), w - wall_t * 2, h - wall_t * 2)
            msp.add_lwpolyline(inner_rect, dxfattribs={'layer': 'WALLS', 'closed': True})

            # Add Hatch between walls
            hatch = msp.add_hatch(dxfattribs={'layer': 'HATCH'})
            hatch.paths.add_polyline_path(outer_rect, is_closed=True)
            hatch.paths.add_polyline_path(inner_rect, is_closed=True)

        # Draw Openings (Professional Doors/Windows)
        for op in r.get('openings', []):
            op_type = op['type']
            wall = op['wall']
            pos = float(op['pos'])
            
            if op_type == 'door':
                size = 0.9
                _draw_door(msp, x, y, w, h, wall, pos, size)
            else:
                size = 1.5
                _draw_window(msp, x, y, w, h, wall, pos, size, wall_t)

        # Label
        msp.add_text(name.upper(), 
                    dxfattribs={'layer': 'ROOM_LABELS', 'height': 0.2, 'insert': (x + w/2, y + h/2)}
                    ).set_placement((x + w/2, y + h/2), align=ezdxf.enums.TextEntityAlignment.CENTER)

    # Save file
    doc.saveas(filename)
    return filename


def _draw_door(msp, x, y, w, h, wall, pos, size):
    # Professional Door with Arc
    attribs = {'layer': 'DOORS', 'color': 4}
    
    if wall == 'north':
        p_base = (x + pos, y + h)
        msp.add_line(p_base, (p_base[0], p_base[1] + size), dxfattribs=attribs) # Leaf
        msp.add_arc(p_base, radius=size, start_angle=0, end_angle=90, dxfattribs=attribs)
    elif wall == 'south':
        p_base = (x + pos + size, y)
        msp.add_line(p_base, (p_base[0], p_base[1] - size), dxfattribs=attribs) # Leaf
        msp.add_arc(p_base, radius=size, start_angle=180, end_angle=270, dxfattribs=attribs)
    elif wall == 'east':
        p_base = (x + w, y + pos)
        msp.add_line(p_base, (p_base[0] + size, p_base[1]), dxfattribs=attribs) # Leaf
        msp.add_arc(p_base, radius=size, start_angle=270, end_angle=0, dxfattribs=attribs)
    elif wall == 'west':
        p_base = (x, y + pos + size)
        msp.add_line(p_base, (p_base[0] - size, p_base[1]), dxfattribs=attribs) # Leaf
        msp.add_arc(p_base, radius=size, start_angle=90, end_angle=180, dxfattribs=attribs)


def _draw_window(msp, x, y, w, h, wall, pos, size, wall_t):
    # Professional Window with Glass Layer
    attribs = {'layer': 'WINDOWS', 'color': 2}
    
    if wall in ['north', 'south']:
        y_coord = y + h if wall == 'north' else y
        msp.add_line((x + pos, y_coord), (x + pos + size, y_coord), dxfattribs=attribs)
        # Detailed center lines (glass)
        msp.add_line((x + pos, y_coord - wall_t/2), (x + pos + size, y_coord - wall_t/2), dxfattribs=attribs)
    else: # east/west
        x_coord = x + w if wall == 'east' else x
        msp.add_line((x_coord, y + pos), (x_coord, y + pos + size), dxfattribs=attribs)
        # Detailed center lines (glass)
        msp.add_line((x_coord - wall_t/2, y + pos), (x_coord - wall_t/2, y + pos + size), dxfattribs=attribs)
