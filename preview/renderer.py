import matplotlib.pyplot as plt
from typing import Dict, Any
import math

def render_preview(spec: Dict[str, Any], filename: str) -> str:
    # Scale: Everything in SPEC is meters, but GENERATOR uses mm.
    # We stay in meters for plotting to keep axis readable, 
    # but we add professional visuals.
    # Master GOST Styles (at 1:100)
    # GOST Paper Sizes (Meters at 1:100)
    PAPERS = {
        'A4_V': (21.0, 29.7),
        'A4_H': (29.7, 21.0),
        'A3': (42.0, 29.7),
        'A2': (59.4, 42.0)
    }
    
    ml, mr, mt, mb = 2.0, 0.5, 0.5, 0.5
    sw_blk, sh_blk = 18.5, 5.5
    
    land_w = float(spec.get('land_width', 10.0))
    land_h = float(spec.get('land_height', 10.0))
    
    # Auto-Select (Match generator.py logic)
    if land_w <= (21.0 - 2.0 - 0.5 - 18.5 - 2.0) and land_h <= (29.7 - 1.0):
        sheet_w, sheet_h = PAPERS['A3']
    elif land_w > 20.0 or land_h > 25.0:
        sheet_w, sheet_h = PAPERS['A2']
    else:
        sheet_w, sheet_h = PAPERS['A3'] 

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor('white')

    # Draw Frame
    ax.add_patch(plt.Rectangle((ml, mb), sheet_w - ml - mr, sheet_h - mt - mb, fill=False, edgecolor='black', linewidth=1.5))

    # GOST Centering (Safe area left of shtamp)
    safe_w = sheet_w - ml - mr - sw_blk - 2.0
    safe_h = sheet_h - mb - mt
    
    ox = ml + (safe_w - land_w)/2
    oy = mb + (safe_h - land_h)/2

    rooms = spec.get('rooms', [])
    for r in rooms:
        x, y = float(r['x']) + ox, float(r['y']) + oy
        w, h = float(r['width']), float(r['height'])
        r_type = r.get('type')
        
        # Professional Master Walls
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, edgecolor='black', linewidth=1.5, zorder=2))
        ax.add_patch(plt.Rectangle((x+0.1, y+0.1), w-0.2, h-0.2, fill=False, edgecolor='black', linewidth=0.5, alpha=0.3, zorder=2))

        # Columns
        for cp in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]:
            ax.add_patch(plt.Rectangle((cp[0]-0.2, cp[1]-0.2), 0.4, 0.4, color='black', alpha=0.8, zorder=5))

        if w > 2.0 and h > 2.0:
            _draw_preview_items_platinum(ax, r_type, x + 0.3, y + 0.3, w)

        if r_type == 'stairs':
            _draw_preview_stairs(ax, x, y, w, h)
        
        # 4. Room Label (with Masking & Dynamic Scaling - Level 5.6)
        name = r.get('name', r_type).upper()
        area_m2 = w * h
        
        # Dynamic Scaling to fit room bounds
        fs = 7 if area_m2 >= 7.5 else 5.5
        
        ax.text(x + w/2, y + h/2, f"{name}\n{area_m2:.1f} m2",
                fontsize=fs, ha='center', va='center', fontweight='medium', color='black',
                zorder=10, bbox={'facecolor': 'white', 'alpha': 0.9, 'edgecolor': 'none', 'pad': 1})

        _draw_preview_dims(ax, x, y, w, h, ox, safe_w, ml, mr, sheet_w)

        for op in r.get('openings', []):
            _draw_preview_opening(ax, x, y, w, h, op)

    # 3. GOST Official Corner Shtamp (185x55mm)
    sx = sheet_w - mr - sw_blk
    sy = mb
    
    # Industrial Tabular Grid
    ax.add_patch(plt.Rectangle((sx, sy), sw_blk, sh_blk, fill=False, edgecolor='black', linewidth=1.2))
    ax.plot([sx, sx + sw_blk], [sy + 1.5, sy + 1.5], color='black', linewidth=0.8)
    ax.plot([sx, sx + sw_blk], [sy + 3.5, sy + 3.5], color='black', linewidth=0.8)
    ax.plot([sx + sw_blk - 5.0, sx + sw_blk - 5.0], [sy, sy + 5.5], color='black', linewidth=0.8)
    ax.plot([sx + sw_blk - 2.5, sx + sw_blk - 2.5], [sy, sy + 1.5], color='black', linewidth=0.8)
    
    # Clean Text (No branding)
    ax.text(sx + 0.5, sy + 4.2, spec.get('style', 'Modern').upper() + " BINO LOYIHASI", fontsize=8, fontweight='bold', ha='left')
    ax.text(sx + sw_blk - 4.5, sy + 4.2, "Masshtab: 1:100", fontsize=6, ha='left')
    ax.text(sx + sw_blk - 2.0, sy + 0.5, "AU-1", fontsize=9, fontweight='bold')

    # Explication Table in Structured Cells
    ye = sy + sh_blk + 1.5 # 15mm padding
    cell_h = 0.8
    ax.text(sx, ye + (len(rooms)+1)*cell_h + 0.2, "XONALARNI EXPLIKATSIYASI", fontsize=9, fontweight='bold')
    ax.plot([sx, sx+sw_blk], [ye, ye], color='black', linewidth=0.8)
    for i, r in enumerate(rooms):
        y_row = ye + (len(rooms)-i)*cell_h
        txt = "{}. {}: {:.1f} m2".format(i+1, r.get('name', r_type).upper(), float(r['width'])*float(r['height']))
        ax.text(sx+0.5, y_row - 0.5, txt, fontsize=6, ha='left')
        ax.plot([sx, sx+sw_blk], [y_row, y_row], color='black', linewidth=0.8)

    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.savefig(filename, dpi=180, bbox_inches='tight')
    plt.close(fig)
    return filename

def _draw_preview_opening(ax, rx, ry, rw, rh, op):
    """Draw professional Door/Window symbols in preview (Level 5.5)."""
    otype = op.get('type', 'door')
    wall = op['wall']
    pos = float(op['pos'])
    w = float(op.get('width', 1.0))
    attr = {'color': 'black', 'linewidth': 0.8}
    
    if wall == 'south': x, y, ang = rx + pos, ry, 0
    elif wall == 'north': x, y, ang = rx + pos, ry + rh, 180
    elif wall == 'west': x, y, ang = rx, ry + pos, 270
    elif wall == 'east': x, y, ang = rx + rw, ry + pos, 90
    else: return

    if otype == 'door':
        # Door Leaf Line
        import math
        leaf_x = x + w * math.cos(math.radians(ang + 30))
        leaf_y = y + w * math.sin(math.radians(ang + 30))
        ax.plot([x, leaf_x], [y, leaf_y], **attr)
        # Swing Arc (Style approximation)
        from matplotlib.patches import Arc
        ax.add_patch(Arc((x, y), 2*w, 2*w, angle=ang, theta1=0, theta2=30, color='black', alpha=0.5, linewidth=0.5))
    else:
        # Window: 3-line glazing
        if wall in ['north', 'south']:
            ax.plot([x-w/2, x+w/2], [y, y], **attr)
            ax.plot([x-w/2, x+w/2], [y+0.1 if wall=='south' else y-0.1, y+0.1 if wall=='south' else y-0.1], color='gray', linewidth=0.4)
            ax.plot([x-w/2, x+w/2], [y+0.2 if wall=='south' else y-0.2, y+0.2 if wall=='south' else y-0.2], **attr)
        else:
            ax.plot([x, x], [y-w/2, y+w/2], **attr)
            ax.plot([x+0.1 if wall=='west' else x-0.1, x+0.1 if wall=='west' else x-0.1], [y-w/2, y+w/2], color='gray', linewidth=0.4)
            ax.plot([x+0.2 if wall=='west' else x-0.2, x+0.2 if wall=='west' else x-0.2], [y-w/2, y+w/2], **attr)

def _draw_preview_dims(ax, x, y, w, h, _ox, _safe_w, _ml, _mr, _sheet_w):
    """Draw professional dimension chains in preview."""
    # Simple detail dimension (Chain 1 approximation)
    yo = y - 0.8
    ax.plot([x, x+w], [yo, yo], color='black', linewidth=0.5)
    # 45-degree ticks
    for px in [x, x+w]:
        ax.plot([px-0.1, px+0.1], [yo-0.1, yo+0.1], color='black', linewidth=0.8)
    ax.text(x+w/2, yo - 0.1, "{:.1f} m".format(w), fontsize=5, ha='center', va='top')

def _draw_preview_items_platinum(ax, r_type, x, y, _w):
    """B&W High-Contrast Furniture Preview."""
    if r_type == 'bedroom':
        ax.add_patch(plt.Rectangle((x, y), 2.0, 1.8, fill=True, color='black', alpha=0.05))
        ax.add_patch(plt.Rectangle((x+0.2, y+1.3), 0.7, 0.4, fill=True, color='black', alpha=0.15))
        ax.add_patch(plt.Rectangle((x+1.1, y+1.3), 0.7, 0.4, fill=True, color='black', alpha=0.15))
    elif r_type in ['bathroom', 'toilet']:
        ax.add_patch(plt.Circle((x+0.3, y+0.2), 0.2, color='black', alpha=0.1))
        ax.add_patch(plt.Rectangle((x, y+0.4), 0.6, 0.2, color='black', alpha=0.05))
    elif r_type == 'kitchen':
        ax.add_patch(plt.Rectangle((x, y), 0.6, 0.6, color='black', alpha=0.05))
        for dx, dy in [(0.15, 0.15), (0.45, 0.15), (0.15, 0.45), (0.45, 0.45)]:
            ax.add_patch(plt.Circle((x+dx, y+dy), 0.05, color='black', alpha=0.2))

def _draw_preview_stairs(ax, x, y, w, h):
    """B&W Industrial Stairs."""
    steps = 12
    sw = w / steps
    for i in range(steps + 1):
        ax.plot([x + i*sw, x + i*sw], [y, y + h], color='black', linewidth=0.5, alpha=0.3)
    ax.plot([x, x+w], [y+h/2, y+h/2], color='black', linewidth=0.5, alpha=0.3)

def _draw_preview_opening(ax, x, y, w, h, op):
    """High-Contrast Openings (B&W)."""
    wall, pos, op_type = op['wall'], float(op['pos']), op['type']
    size = 0.9 if op_type == 'door' else 1.5
    lw = 3
    
    if wall == 'north': 
        ax.plot([x + pos, x + pos + size], [y + h, y + h], color='white', linewidth=lw+2, zorder=3)
        ax.plot([x + pos, x + pos + size], [y + h, y + h], color='black', linewidth=lw, zorder=4)
    elif wall == 'south': 
        ax.plot([x + pos, x + pos + size], [y, y], color='white', linewidth=lw+2, zorder=3)
        ax.plot([x + pos, x + pos + size], [y, y], color='black', linewidth=lw, zorder=4)
    elif wall == 'east': 
        ax.plot([x + w, x + w], [y + pos, y + pos + size], color='white', linewidth=lw+2, zorder=3)
        ax.plot([x + w, x + w], [y + pos, y + pos + size], color='black', linewidth=lw, zorder=4)
    elif wall == 'west': 
        ax.plot([x, x], [y + pos, y + pos + size], color='white', linewidth=lw+2, zorder=3)
        ax.plot([x, x], [y + pos, y + pos + size], color='black', linewidth=lw, zorder=4)
