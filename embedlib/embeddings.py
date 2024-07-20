import os
import requests
import json
def get_embeddings(content):
    try:
        url = f"http://{os.environ['LLM_BACKEND']}:{os.environ['LLM_BACKEND_PORT']}/api/embeddings"
        payload = {
            "model": os.environ['EMBEDDING_MODEL'],
            "prompt": content
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}") 