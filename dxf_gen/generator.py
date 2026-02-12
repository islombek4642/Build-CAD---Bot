import ezdxf
from ezdxf.entities import LWPolyline
from typing import Dict, Any, List, Tuple
from dxf_gen.components import room_rectangle
from config import settings

def _add_layer(doc, name: str, color: int = 7, linetype: str = 'CONTINUOUS'):
    if name not in doc.layers:
        doc.layers.new(name=name, dxfattribs={'color': color, 'linetype': linetype})

def create_plan(spec: Dict[str, Any], filename: str) -> str:
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Define Platinum Layers
    _add_layer(doc, 'A-WALL-EXTR', color=7)     # Outer Walls
    _add_layer(doc, 'A-WALL-INTR', color=253)   # Inner Walls
    _add_layer(doc, 'A-COLS', color=1)          # Columns (Red)
    _add_layer(doc, 'A-DOOR', color=4)          # Doors
    _add_layer(doc, 'A-WIND', color=2)          # Windows
    _add_layer(doc, 'A-STAI', color=5)          # Stairs
    _add_layer(doc, 'A-FURN', color=251)        # Furniture (Gray)
    _add_layer(doc, 'A-PLUM', color=140)        # Plumbing (Blue-ish)
    _add_layer(doc, 'A-ANNO-TEXT', color=3)     # Labels
    _add_layer(doc, 'A-ANNO-DIMS', color=1)     # Dimensions
    _add_layer(doc, 'A-ANNO-AXES', color=8, linetype='DASHED')
    _add_layer(doc, 'A-TITLE-BLOCK', color=7)

    land_w_m = float(spec.get('land_width', 10.0))
    land_h_m = float(spec.get('land_height', 10.0))

    # Smarter Scaling (Level 5.7)
    # If project fits A3 at 1:50, use it for better sheet fill
    if land_w_m <= 15.0 and land_h_m <= 25.0:
        sheet_w, sheet_h = 42000, 29700 # A3
        SCALE = 2000 # 1:50 scale
    elif land_w_m > 25.0 or land_h_m > 35.0:
        sheet_w, sheet_h = 59400, 42000 # A2
        SCALE = 1000 # 1:100 scale
    else:
        sheet_w, sheet_h = 42000, 29700 # A3
        SCALE = 1000 # 1:100 scale

    FONT_SUB = 2.5 * (SCALE/100)
    FONT_MAIN = 3.5 * (SCALE/100)
    wall_ext = 380 
    wall_int = 120 

    # GOST Paper Sizes (mm)
    # Define Professional Text Style
    if 'GOST_STYLE' not in doc.styles:
        doc.styles.new('GOST_STYLE', dxfattribs={'font': 'isocp.shx', 'width': 0.8})

    margin_l, margin_r, margin_t, margin_b = 2000, 500, 500, 500
    sw_mm = 18500

    # Top-Left Positioning (Level 5.7)
    offset_x = margin_l
    offset_y = sheet_h - margin_t - (land_h_m * SCALE)
    
    _draw_gost_frame(msp, sheet_w, sheet_h, margin_l, margin_r, margin_t, margin_b)
    _draw_pro_axes(msp, land_w_m * SCALE, land_h_m * SCALE, offset_x, offset_y)

    rooms = spec.get('rooms', [])
    for r in rooms:
        x, y = float(r['x']) * SCALE + offset_x, float(r['y']) * SCALE + offset_y
        w, h = float(r['width']) * SCALE, float(r['height']) * SCALE
        r_type = r.get('type')
        
        # Professional Wall Logic with Hatching
        is_extr = (float(r['x']) < 0.1 or float(r['y']) < 0.1 or float(r['x'])+float(r['width']) > float(spec.get('land_width')) - 0.5)
        layer = 'A-WALL-EXTR' if is_extr else 'A-WALL-INTR'
        outer_pts = room_rectangle((x, y), w, h)
        inner_pts = room_rectangle((x + wall_int, y + wall_int), w - wall_int*2, h - wall_int*2)
        
        msp.add_lwpolyline(outer_pts, dxfattribs={'layer': layer, 'closed': True})
        hatch = msp.add_hatch(dxfattribs={'layer': layer, 'color': 252})
        hatch.set_pattern_fill('ANSI31', scale=50)
        hatch.paths.add_polyline_path(outer_pts, is_closed=True)
        hatch.paths.add_polyline_path(inner_pts, is_closed=True)
        
        # Columns (High-fidelity 400x400)
        for cp in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]:
            msp.add_lwpolyline(room_rectangle((cp[0]-200, cp[1]-200), 400, 400), dxfattribs={'layer': 'A-COLS', 'closed': True})

        # High-Detail Furniture/Plumbing
        _draw_platinum_items(msp, r_type, x + 600, y + 600, w)

        if r_type == 'stairs':
            _draw_pro_stairs(msp, x, y, w, h)
        
        # 3. Openings with High Fidelity Symbols
        for op in r.get('openings', []):
            _draw_pro_opening(msp, x, y, w, h, op, wall_ext)

        # 4. Room Label (MText with Masking & Dynamic Scaling)
        name = r.get('name', r_type).upper()
        area_m2 = (w * h) / 1e6
        
        # Dynamic Scaling: use smaller font for compact rooms
        h_font = FONT_MAIN if area_m2 >= 7.5 else FONT_SUB
        
        label_text = f"{name}\\P{area_m2:.1f} m2"
        mtext = msp.add_mtext(label_text, dxfattribs={
            'layer': 'A-ANNO-TEXT', 
            'char_height': h_font, 
            'style': 'GOST_STYLE'
        })
        # Background Masking (Level 5.6)
        mtext.set_bg_color('canvas', scale=1.2)
        mtext.set_location((x+w/2, y+h/2), attachment_point=ezdxf.enums.MTextEntityAlignment.MIDDLE_CENTER)

    # 5. External Dimension Chains (Level 5.4)
    _draw_gost_dimension_chains(msp, rooms, land_w_m * SCALE, land_h_m * SCALE, offset_x, offset_y)

    # 3. GOST Official Corner Shtamp (185x55mm)
    _draw_gost_corner_shtamp(msp, sheet_w, margin_r, margin_b, rooms, spec, FONT_SUB, FONT_MAIN)

    doc.saveas(filename)
    return filename


def _draw_platinum_items(msp, r_type, x, y, w):
    """Draw high-detail blocks like beds with pillows, WC with tank, etc."""
    attr_furn = {'layer': 'A-FURN'}
    attr_plum = {'layer': 'A-PLUM'}
    if r_type == 'bedroom' and w > 3000:
        # Bed with Pillows (2000x1800)
        msp.add_lwpolyline(room_rectangle((x, y), 2000, 1800), dxfattribs=attr_furn)
        msp.add_lwpolyline(room_rectangle((x+200, y+1300), 700, 400), dxfattribs=attr_furn) # Pillow 1
        msp.add_lwpolyline(room_rectangle((x+1100, y+1300), 700, 400), dxfattribs=attr_furn) # Pillow 2
    elif r_type in ['bathroom', 'toilet']:
        # WC: Tank + Bowl
        msp.add_lwpolyline(room_rectangle((x, y+400), 600, 200), dxfattribs=attr_plum) # Tank
        msp.add_ellipse((x+300, y+200), major_axis=(200, 0), ratio=1.5, dxfattribs=attr_plum) # Bowl
    elif r_type == 'kitchen':
        # Stove with 4 burners
        msp.add_lwpolyline(room_rectangle((x, y), 600, 600), dxfattribs=attr_furn)
        for dx, dy in [(150, 150), (450, 150), (150, 450), (450, 450)]:
            msp.add_circle((x+dx, y+dy), radius=60, dxfattribs=attr_furn)

def _draw_pro_stairs(msp, x, y, w, h):
    attr = {'layer': 'A-STAI'}
    steps = 15
    sw = w / steps
    for i in range(steps + 1):
        msp.add_line((x+i*sw, y), (x+i*sw, y+h), dxfattribs=attr)
    # Mid-flight landing line
    center_y = y + h/2
    msp.add_line((x, center_y), (x+w, center_y), dxfattribs=attr)
    # Directional Circle with Arrow
    msp.add_circle((x+300, center_y), radius=100, dxfattribs=attr)
    msp.add_line((x+300, center_y), (x+w-300, center_y), dxfattribs=attr)

def _draw_pro_opening(msp, rx, ry, rw, rh, op, wall_thick):
    """Draw professional Door/Window symbols (Level 5.5)."""
    otype = op.get('type', 'door')
    wall = op['wall']
    pos = float(op['pos']) * 1000
    w = float(op.get('width', 0.9 if otype=='door' else 1.2)) * 1000
    attr = {'layer': 'A-DOOR' if otype=='door' else 'A-GLAZ', 'lineweight': 20}
    
    # Calculate opening center point
    if wall == 'south': x, y, ang = rx + pos, ry, 0
    elif wall == 'north': x, y, ang = rx + pos, ry + rh, 180
    elif wall == 'west': x, y, ang = rx, ry + pos, 270
    elif wall == 'east': x, y, ang = rx + rw, ry + pos, 90
    else: return

    if otype == 'door':
        # Door Leaf at 30 degrees (Standard GOST)
        import math
        leaf_angle = math.radians(ang + 30)
        msp.add_line((x, y), (x + w*math.cos(leaf_angle), y + w*math.sin(leaf_angle)), dxfattribs=attr)
        # Swing Arc
        msp.add_arc((x, y), radius=w, start_angle=ang, end_angle=ang+30, dxfattribs={**attr, 'lineweight': 15})
    else:
        # Window: 3-line glazing symbol
        if wall in ['north', 'south']:
            msp.add_line((x-w/2, y), (x+w/2, y), dxfattribs=attr) # Outer
            msp.add_line((x-w/2, y+wall_thick/2), (x+w/2, y+wall_thick/2) if wall=='south' else (x+w/2, y-wall_thick/2), dxfattribs={**attr, 'lineweight': 10}) # Glazing
        else:
            msp.add_line((x, y-w/2), (x, y+w/2), dxfattribs=attr) # Outer
            msp.add_line((x+wall_thick/2 if wall=='west' else x-wall_thick/2, y-w/2), (x+wall_thick/2 if wall=='west' else x-wall_thick/2, y+w/2), dxfattribs={**attr, 'lineweight': 10})

def _draw_gost_dimension_chains(msp, rooms, tw, th, ox, oy):
    """Implement Professional Orthogonal Multi-row Chains (Level 5.8)."""
    # 1. External Bottom Chain (Distances from left frame)
    d1 = 1200 # 12mm from building
    d2 = 1900 # 19mm total (7mm gap)
    
    # Overall Dimension (Strictly Horizontal)
    _add_gost_dim(msp, (ox, oy), (ox+tw, oy), -d2, "{}".format(int(tw)))
    
    # Internal parts (Sorted uniquely)
    x_coords = sorted(list(set([r['x']*1000 for r in rooms] + [(r['x']+r['width'])*1000 for r in rooms])))
    for i in range(len(x_coords)-1):
        x1, x2 = x_coords[i], x_coords[i+1]
        dist = x2 - x1
        if dist > 300: # ignore tiny gaps
            # Force strictly horizontal dim
            _add_gost_dim(msp, (ox+x1, oy), (ox+x2, oy), -d1, "{}".format(int(dist)))

def _add_gost_dim(msp, p1, p2, dist, text):
    """Helper for GOST dimensions with Ticks."""
    dim = msp.add_aligned_dim(p1=p1, p2=p2, distance=dist, 
                              dxfattribs={'layer': 'A-ANNO-DIMS'})
    dim.set_tick(size=300) # 3mm tick
    dim.set_text(text)

def _draw_gost_frame(msp, w, h, ml, mr, mt, mb):
    attr = {'layer': 'A-TITLE-BLOCK'}
    # Internal frame only (20/5/5/5). Outer boundary removed per Level 5.2.
    msp.add_lwpolyline([(ml, mb), (w-mr, mb), (w-mr, h-mt), (ml, h-mt)], dxfattribs={**attr, 'closed': True, 'color': 7, 'lineweight': 50})

def _draw_pro_axes(msp, w, h, ox, oy):
    attr = {'layer': 'A-ANNO-AXES'}
    msp.add_line((ox-1000, oy), (ox+w+1000, oy), dxfattribs=attr)
    msp.add_line((ox, oy-1000), (ox, oy+h+1000), dxfattribs=attr)
    msp.add_text("1", dxfattribs={'height': 300, 'insert': (ox, oy-1500)})
    msp.add_text("A", dxfattribs={'height': 300, 'insert': (ox-1500, oy)})

def _draw_gost_corner_shtamp(msp, sw, mr, mb, rooms, spec, fsub, fmain):
    """GOST 21.1101 Form 1 (Clean Industrial Release)."""
    w, h = 18500, 5500
    x0, y0 = sw - mr - w, mb
    attr = {'layer': 'A-TITLE-BLOCK', 'lineweight': 30}
    
    # Full Tabular Grid
    msp.add_lwpolyline([(x0, y0), (x0+w, y0), (x0+w, y0+h), (x0, y0+h)], dxfattribs={**attr, 'closed': True})
    # Horizontal Dividers
    msp.add_line((x0, y0+1500), (x0+w, y0+1500), dxfattribs=attr)
    msp.add_line((x0+w-5000, y0+3500), (x0+w, y0+3500), dxfattribs=attr)
    # Vertical Dividers
    msp.add_line((x0+w-5000, y0), (x0+w-5000, y0+h), dxfattribs=attr)
    msp.add_line((x0+w-2500, y0), (x0+w-2500, y0+1500), dxfattribs=attr)
    
    # Clean Text (No branding)
    title = spec.get('style', 'Modern').upper() + " BINO LOYIHASI"
    msp.add_text(title, dxfattribs={**attr, 'height': fmain, 'insert': (x0+200, y0+3500)})
    msp.add_text("Masshtab: 1:100", dxfattribs={**attr, 'height': fsub, 'insert': (x0+w-4800, y0+3700)})
    msp.add_text("Varaq: AU-01", dxfattribs={**attr, 'height': fsub, 'insert': (x0+w-2300, y0+500)})

    # Room Explication in Matching Table
    ye = y0 + h + 1500 # 15mm padding from shtamp
    cell_h = 600
    msp.add_text("XONALARNI EXPLIKATSIYASI", dxfattribs={**attr, 'height': fmain, 'insert': (x0, ye + (len(rooms)+1)*cell_h)})
    # Draw explication grid
    msp.add_line((x0, ye), (x0+w, ye), dxfattribs=attr) # Base
    for i, r in enumerate(rooms):
        y_row = ye + (len(rooms)-i)*cell_h
        area = (float(r['width']) * float(r['height'])) / 1e6
        txt = "{}. {}: {:.1f} m2".format(i+1, r.get('name', r['type']).upper(), area)
        msp.add_text(txt, dxfattribs={**attr, 'height': fsub, 'insert': (x0+200, y_row - 400)})
        msp.add_line((x0, y_row), (x0+w, y_row), dxfattribs=attr)
