"""Shared test data: the static JSONPlaceholder dataset and write payloads."""

# resource -> number of items in the static dataset
COUNTS = {
    "posts": 100,
    "comments": 500,
    "albums": 100,
    "photos": 5000,
    "todos": 200,
    "users": 10,
}

RESOURCES = list(COUNTS)

# resource -> (payload for POST/PUT, field to PATCH)
WRITE_DATA = {
    "posts": ({"userId": 1, "title": "t", "body": "b"}, "title"),
    "comments": ({"postId": 1, "name": "n", "email": "a@b.com", "body": "b"}, "name"),
    "albums": ({"userId": 1, "title": "t"}, "title"),
    "photos": ({"albumId": 1, "title": "t", "url": "http://x/y.png", "thumbnailUrl": "http://x/t.png"}, "title"),
    "todos": ({"userId": 1, "title": "t", "completed": False}, "title"),
    "users": ({"name": "n", "username": "u", "email": "a@b.com"}, "name"),
}


def next_id(resource: str) -> int:
    """Id the API assigns to a newly created item (writes are never persisted)."""
    return COUNTS[resource] + 1
