import requests

api_key = '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'
url = 'https://api.openai.com/v1/chat/completions'

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

data = {
    'model': 'gpt-4',
    'messages': [
        {'role': 'user', 'content': 'Ciao, come stai?'}
    ],
    'max_tokens': 50,
    'temperature': 0.7
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    response_text = response.json()
    print(response_text['choices'][0]['message']['content'].strip())
else:
    print(f"Errore: {response.status_code}")
    print(response.text)