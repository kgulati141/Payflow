import json

from app.database.redis import get_redis


def set_value(key: str, value: str):
    redis_client = get_redis()
    redis_client.set(key, value)


def get_value(key: str):
    redis_client = get_redis()
    return redis_client.get(key)


def delete_value(key: str):
    redis_client = get_redis()
    return redis_client.delete(key)


def key_exists(key: str):
    redis_client = get_redis()
    return redis_client.exists(key)


def set_expiry(key: str, seconds: int):
    redis_client = get_redis()
    return redis_client.expire(key, seconds)


def set_json(key: str, value: dict, expiry: int = 300):
    redis_client = get_redis()

    redis_client.set(
        key,
        json.dumps(value),
        ex=expiry
    )


def get_json(key: str):
    redis_client = get_redis()

    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)