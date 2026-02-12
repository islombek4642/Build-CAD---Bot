import os
import json
import requests
from typing import Dict, Any
from config import settings


class LLMClient:
    def __init__(self, provider: str = None, api_key: str = None, endpoint: str = None):
        self.provider = provider or settings.AI_PROVIDER
        self.api_key = api_key or settings.AI_API_KEY
        self.endpoint = endpoint or settings.AI_ENDPOINT

    def parse_to_json(self, prompt: str) -> Dict[str, Any]:
        # Use Groq API for strict JSON output
        if self.provider == 'mock' or not self.api_key:
            return self._mock_response(prompt)

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'llama-3.3-70b-versatile',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'response_format': {'type': 'json_object'},
            'max_completion_tokens': 800
        }
        endpoint = self.endpoint or 'https://api.groq.com/openai/v1/chat/completions'
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Extract JSON from Groq response
        try:
            content = data['choices'][0]['message']['content']
            return json.loads(content)
        except Exception:
            # fallback: try to find JSON block in content
            text = data['choices'][0]['message']['content']
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            raise

    def _mock_response(self, prompt: str) -> Dict[str, Any]:
        # Mock response matching the new schema
        return {
            'total_area': 100.0,
            'land_width': 10.0,
            'land_height': 10.0,
            'floor_count': 1,
            'rooms': [
                {'name': 'Living Room', 'type': 'living_room', 'x': 0, 'y': 0, 'width': 5, 'height': 5, 'separate': False},
                {'name': 'Bedroom 1', 'type': 'bedroom', 'x': 5, 'y': 0, 'width': 5, 'height': 5, 'separate': True},
                {'name': 'Kitchen', 'type': 'kitchen', 'x': 0, 'y': 5, 'width': 5, 'height': 5, 'separate': False}
            ],
            'entrance': 'south',
            'walls_thickness': 0.3,
            'notes': 'Mock layout'
        }


llm_client = LLMClient()
