import redis
from redis.commands.json.path import Path

r = redis.Redis.from_url("redis://localhost:6379")

for key in r.scan_iter("chat:*"):
    print(f"\n==== {key.decode()} ====")
    data = r.json().get(key, Path.root_path())
    print(data)
