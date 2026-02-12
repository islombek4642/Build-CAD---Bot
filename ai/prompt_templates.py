SCHEMA_PROMPT = '''
Convert user architectural requirements into a PLATINUM LEVEL professional CAD JSON.
The output will be rendered as a high-fidelity blueprint with "uz.archdesign" vertical title block and detailed blocks.

ARCHITECTURAL RULES (PLATINUM STANDARDS):
1. PACKING: Rooms must be tightly packed with ZERO gaps or overlaps.
2. HALLS: Main corridors should be 1.2m to 2.0m wide for professional flow.
3. CONNECTIVITY: Every room MUST connect to a hall/corridor via a door.
4. STAIRS: For multistory plans, place a 3x2m stairs block in the entrance hall.
5. WINDOWS: Place on EXTERIOR walls only. Minimum 1.5m width for living rooms.
6. STYLE: If user says "Modern", use large windows and open-plan kitchen/living layouts.

JSON SCHEMA:
{
  "total_area": "number",
  "land_width": "number",
  "land_height": "number",
  "floor_count": "integer",
  "style": "Modern|Classic",
  "rooms": [
    {
      "name": "string",
      "type": "bedroom|living_room|kitchen|bathroom|hall|stairs|office|gym|other",
      "x": "number", "y": "number", "width": "number", "height": "number",
      "openings": [
        {"type": "door|window", "wall": "north|south|east|west", "pos": "number"}
      ]
    }
  ],
  "entrance": "north|south|east|west",
  "walls_thickness": "number"
}

Step 1: Layout the Hall/Stairs first (the skeleton).
Step 2: Pack specialty rooms around the hall (Bedroom, Living, etc.).
Step 3: Add Openings (Doors internal, Windows external).
Step 4: Return JSON only.
'''
