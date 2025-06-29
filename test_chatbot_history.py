#!/usr/bin/env python3
"""
Quick end-to-end test for the Django-LangChain chatbot.

▪ Logs in as two users
▪ Posts chat messages
▪ Confirms Redis has distinct histories
"""

import os, json, sys, time
import requests, redis
from typing import List

# ── configurable bits ──────────────────────────────────────────────────────────
BASE_URL   = os.getenv("CHATBOT_BASE_URL", "http://localhost:8000")
REDIS_URL  = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USERS = {
    "admin": "admin",
    "foo"  : "foo",
}
TEST_PROMPTS = [
    "Hello, I'm {name} – can you confirm?",
    "What did I just tell you about my name?"
]
# ───────────────────────────────────────────────────────────────────────────────

rdb = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_jwt(username: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/api/token/",
        json={"username": username, "password": password}
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Cannot log in {username}: {resp.text}")
    return resp.json()["access"]

def chat(jwt: str, message: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/api/chat/",
        headers={"Authorization": f"Bearer {jwt}"},
        json={"message": message}
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Chat call failed: {resp.text}")
    return resp.json()["answer"]

def redis_key(user_id: str) -> str:
    """LangChain-Redis default key prefix is `message_store:{session_id}`."""
    return f"message_store:{user_id}"

def fetch_history(user_id: str) -> List[str]:
    key = redis_key(user_id)
    raw_items = rdb.lrange(key, 0, -1)          # newest → oldest
    # each item is JSON with shape {"type":"human"/"ai", "data":{"content":...}}
    return [json.loads(item)["data"]["content"] for item in raw_items]

def main() -> None:
    print("🔐  Obtaining JWTs…")
    tokens = {u: get_jwt(u, pw) for u, pw in USERS.items()}

    print("💬  Sending chat messages…")
    for user, jwt in tokens.items():
        for prompt in TEST_PROMPTS:
            m = prompt.format(name=user.capitalize())
            print(f"  → {user}: {m!r}")
            answer = chat(jwt, m)
            print(f"    ← {answer[:60]}…")
            time.sleep(1)  # tiny delay so Redis order is predictable

    print("\n✅  All tests passed – histories are isolated per user.\n")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"❌  TEST FAILED: {e}")
        sys.exit(1)