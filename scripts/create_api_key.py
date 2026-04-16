"""
Run this once to create your first API key.
Usage: python scripts/create_api_key.py "my-key-name"
"""
import sys
import os
import secrets
import psycopg2
from dotenv import load_dotenv

load_dotenv()

name = sys.argv[1] if len(sys.argv) > 1 else "default"
key = secrets.token_urlsafe(32)

conn = psycopg2.connect(os.environ["DATABASE_URL"])
with conn.cursor() as cur:
    cur.execute("INSERT INTO api_keys (key, name) VALUES (%s, %s)", (key, name))
conn.commit()
conn.close()

print(f"API key created for '{name}':")
print(key)
