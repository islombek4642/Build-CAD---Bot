import matplotlib.pyplot as plt
from typing import Dict, Any
import math


def render_preview(spec: Dict[str, Any], filename: str) -> str:
    land_w = float(spec.get('land_width', 10.0))
    land_h = float(spec.get('land_height', 10.0))

    fig, ax = plt.subplots(figsize=(8, 8))
    # Outer land boundary
    ax.plot([0, land_w, land_w, 0, 0], [0, 0, land_h, land_h, 0], color='gray', linestyle='--')

    rooms = spec.get('rooms', [])
    for r in rooms:
        x, y = float(r['x']), float(r['y'])
        w, h = float(r['width']), float(r['height'])
        
        rect_x = [x, x + w, x + w, x, x]
        rect_y = [y, y, y + h, y + h, y]
        ax.plot(rect_x, rect_y, color='black', linewidth=1.5) # Black walls
        
        # Professional openings in preview
        for op in r.get('openings', []):
            wall = op['wall']
            pos = float(op['pos'])
            size = 0.9 if op['type'] == 'door' else 1.5
            color = 'cyan' if op['type'] == 'door' else 'yellow'
            
            if op['type'] == 'door':
                # Simplified "arc" for door in matplotlib
                if wall == 'north':
                    ax.plot([x + pos, x + pos], [y + h, y + h + size], color=color, linewidth=2)
                    ax.add_patch(plt.Circle((x + pos, y + h), size, color=color, fill=False, linestyle=':', alpha=0.5))
                elif wall == 'south':
                    ax.plot([x + pos + size, x + pos + size], [y, y - size], color=color, linewidth=2)
                    ax.add_patch(plt.Circle((x + pos + size, y), size, color=color, fill=False, linestyle=':', alpha=0.5))
                elif wall == 'east':
                    ax.plot([x + w, x + w + size], [y + pos, y + pos], color=color, linewidth=2)
                    ax.add_patch(plt.Circle((x + w, y + pos), size, color=color, fill=False, linestyle=':', alpha=0.5))
                elif wall == 'west':
                    ax.plot([x, x - size], [y + pos + size, y + pos + size], color=color, linewidth=2)
                    ax.add_patch(plt.Circle((x, y + pos + size), size, color=color, fill=False, linestyle=':', alpha=0.5))
            else: # window
                if wall == 'north':
                    ax.plot([x + pos, x + pos + size], [y + h, y + h], color=color, linewidth=4)
                elif wall == 'south':
                    ax.plot([x + pos, x + pos + size], [y, y], color=color, linewidth=4)
                elif wall == 'east':
                    ax.plot([x + w, x + w], [y + pos, y + pos + size], color=color, linewidth=4)
                elif wall == 'west':
                    ax.plot([x, x], [y + pos, y + pos + size], color=color, linewidth=4)

        name = r.get('name', r.get('type', 'room'))
        ax.text(x + w/2, y + h/2, name.upper(), 
                fontsize=8, ha='center', va='center', fontweight='bold')

    ax.set_xlim(-1, land_w + 1)
    ax.set_ylim(-1, land_h + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename
