import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('XAI_API_KEY', '').strip()

# Try different model names
models = ['grok-2', 'grok-vision-beta', 'grok', 'grok-3']

for model in models:
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': 'Say hi'}],
        'stream': False,
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post('https://api.x.ai/v1/chat/completions', json=payload, headers=headers, timeout=10)
        print(f"{model}: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  ✓ SUCCESS - Use this model name!")
        else:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"{model}: {str(e)}")