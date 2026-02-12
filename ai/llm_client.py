import os
import json
import requests
import logging
from typing import Dict, Any
from config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, provider: str = None, api_key: str = None, endpoint: str = None):
        self.provider = provider or settings.AI_PROVIDER
        self.api_key = api_key or settings.AI_API_KEY
        self.endpoint = endpoint or settings.AI_ENDPOINT

    def parse_to_json(self, prompt: str) -> Dict[str, Any]:
        # Log which provider is being used
        if self.provider == 'mock' or not self.api_key:
            logger.info("Using MOCK AI provider (Professional Template)")
            return self._mock_response()

        logger.info(f"Using REAL AI provider: {self.provider}")
        # ... logic for real API ...
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [{'role': 'user', 'content': prompt}],
            'response_format': {'type': 'json_object'},
            'max_completion_tokens': 1000
        }
        endpoint = self.endpoint or 'https://api.groq.com/openai/v1/chat/completions'
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        try:
            content = data['choices'][0]['message']['content']
            return json.loads(content)
        except Exception:
            text = data['choices'][0]['message']['content']
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            raise

    def _mock_response(self) -> Dict[str, Any]:
        # Return a HIGHLY PROFESSIONAL complex villa plan (15x25m)
        return {
            'total_area': 160.0,
            'land_width': 15.0, # As requested by user
            'land_height': 25.0,
            'floor_count': 2,
            'style': 'Modern',
            'rooms': [
                {
                    'name': 'Dahliz (Entrance Hall)', 
                    'type': 'hall', 
                    'x': 5, 'y': 0, 'width': 5, 'height': 4,
                    'openings': [{'type': 'door', 'wall': 'south', 'pos': 2.0}]
                },
                {
                    'name': 'Zinapoya (Stairs)', 
                    'type': 'stairs', 
                    'x': 5, 'y': 4, 'width': 3, 'height': 2,
                    'openings': [{'type': 'door', 'wall': 'south', 'pos': 1.0}]
                },
                {
                    'name': 'Mehmonxona (Modern Living)', 
                    'type': 'living_room', 
                    'x': 0, 'y': 6, 'width': 8, 'height': 6,
                    'openings': [
                        {'type': 'door', 'wall': 'south', 'pos': 4.0},
                        {'type': 'window', 'wall': 'north', 'pos': 2.0},
                        {'type': 'window', 'wall': 'north', 'pos': 5.0}
                    ]
                },
                {
                    'name': 'Oshxona (Kitchen Studio)', 
                    'type': 'kitchen', 
                    'x': 8, 'y': 6, 'width': 6, 'height': 6,
                    'openings': [{'type': 'door', 'wall': 'west', 'pos': 2.0}, {'type': 'window', 'wall': 'north', 'pos': 2.0}]
                },
                {
                    'name': 'Yotoqxona (Master Bed)', 
                    'type': 'bedroom', 
                    'x': 10, 'y': 0, 'width': 5, 'height': 5,
                    'openings': [{'type': 'door', 'wall': 'west', 'pos': 1.0}, {'type': 'window', 'wall': 'east', 'pos': 2.0}]
                },
                {
                    'name': 'Trenajyor Zal (Gym)', 
                    'type': 'gym', 
                    'x': 0, 'y': 0, 'width': 5, 'height': 5,
                    'openings': [{'type': 'door', 'wall': 'east', 'pos': 2.0}]
                }
            ],
            'entrance': 'south',
            'walls_thickness': 0.38
        }

llm_client = LLMClient()
