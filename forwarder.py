import requests
import os

ANYTHING_INGEST_URL = os.getenv("ANYTHING_INGEST_URL")

def forward_to_anything(data: dict):
    if not ANYTHING_INGEST_URL:
        raise Exception("ANYTHING_INGEST_URL not set")

    response = requests.post(ANYTHING_INGEST_URL, json=data)

    if response.status_code != 200:
        raise Exception(f"Forwarding failed: {response.text}")
