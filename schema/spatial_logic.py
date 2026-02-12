from typing import Dict, Any, List, Tuple

def check_overlaps(rooms: List[Dict[str, Any]]) -> List[str]:
    """Detect overlapping rooms and return error messages."""
    errors = []
    for i, r1 in enumerate(rooms):
        for j, r2 in enumerate(rooms):
            if i >= j: continue
            
            x1, y1 = float(r1['x']), float(r1['y'])
            w1, h1 = float(r1['width']), float(r1['height'])
            
            x2, y2 = float(r2['x']), float(r2['y'])
            w2, h2 = float(r2['width']), float(r2['height'])
            
            # Simple rectangle intersection
            if not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1):
                # Tolerance check (e.g. 0.01m overlap might be rounding error)
                overlap_w = min(x1 + w1, x2 + w2) - max(x1, x2)
                overlap_h = min(y1 + h1, y2 + h2) - max(y1, y2)
                if overlap_w > 0.05 and overlap_h > 0.05:
                    n1 = r1.get('name', f"Room {i}")
                    n2 = r2.get('name', f"Room {j}")
                    errors.append(f"{n1} and {n2} overlap by {overlap_w:.2f}m x {overlap_h:.2f}m")
    return errors

def check_connectivity(rooms: List[Dict[str, Any]]) -> List[str]:
    """Check if rooms are connected (have doors/openings to other rooms or exterior)."""
    # This is a bit more complex, for now we just check if every room has at least one door
    errors = []
    for i, r in enumerate(rooms):
        doors = [op for op in r.get('openings', []) if op['type'] == 'door']
        if not doors:
            name = r.get('name', f"Room {i}")
            errors.append(f"{name} has no doors - it must be accessible.")
    return errors

def validate_spatial_integrity(data: Dict[str, Any]):
    """Run all spatial checks."""
    rooms = data.get('rooms', [])
    errors = []
    errors.extend(check_overlaps(rooms))
    errors.extend(check_connectivity(rooms))
    
    # Check if rooms are within land boundaries
    land_w = float(data.get('land_width', 0))
    land_h = float(data.get('land_height', 0))
    for i, r in enumerate(rooms):
        x, y = float(r['x']), float(r['y'])
        w, h = float(r['width']), float(r['height'])
        if x < 0 or y < 0 or x + w > land_w or y + h > land_h:
            name = r.get('name', f"Room {i}")
            errors.append(f"{name} is outside land boundaries ({land_w}x{land_h}).")
            
    if errors:
        raise ValueError("\n".join(errors))
