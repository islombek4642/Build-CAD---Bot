SCHEMA_PROMPT = '''
Convert the user architectural requirements into a strict JSON document matching this schema:

{
  "total_area": "number (sq.m, calculate from land_width * land_height)",
  "land_width": "number (meters)",
  "land_height": "number (meters)",
  "floor_count": "integer (default 1)",
  "rooms": [
    {
      "name": "string (e.g. 'Master Bedroom')",
      "type": "string (bedroom|living_room|kitchen|bathroom|other)",
      "x": "number (bottom-left x coordinate in meters)",
      "y": "number (bottom-left y coordinate in meters)",
      "width": "number (room width in meters)",
      "height": "number (room height in meters)",
      "separate": "boolean (default false)",
      "openings": [
        {
          "type": "string (door|window)",
          "wall": "string (north|south|east|west)",
          "pos": "number (offset from start of wall clockwise, e.g. for north wall it is offset from left corner)"
        }
      ]
    }
  ],
  "entrance": "string (north|south|east|west, default south)",
  "walls_thickness": "number (default 0.3)",
  "notes": "optional string"
}

IMPORTANT: 
- All rooms must be within [0, land_width] and [0, land_height].
- Rooms must not overlap significantly.
- Provide a realistic layout for a functional home.
- CONSIDER THE FOLLOWING CATEGORIES FROM USER NOTES:
  1. General Info: Land shape, address impacts (if any), floor area.
  2. Room Composition: Number of bedrooms/bathrooms, specific room sizes requested, garage, terrace/balcony.
  3. Style & Design: Minimalism/Classic/National style (reflect in proportions), roof type (note in JSON), materials (note in JSON).
  4. Budget & Materials: Standard/Premium (reflect in room count/sizes if constrained).
  5. Technical Requirements: Sunlight orientation (place windows on sunny sides), seismic resistance (functional layout).
  6. Documents & Regulations: Adhere to land dimensions provided.
  7. Special Wishes: Open/closed kitchen, panoramic windows (large windows in JSON), smart home hubs.
Return only valid JSON and nothing else.
'''
