"""JSON schemas for all six resources.

Every object sets additionalProperties: False, so an unexpected new field in
the API response fails the test instead of slipping through.
"""

EMAIL = {"type": "string", "pattern": r"^[^@\s]+@[^@\s]+\.[^@\s]+$"}
URL = {"type": "string", "pattern": r"^https?://"}


def _object(properties: dict) -> dict:
    """Strict object schema: all listed properties required, no extras allowed."""
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


POST_SCHEMA = _object(
    {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
    }
)

COMMENT_SCHEMA = _object(
    {
        "postId": {"type": "integer"},
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": EMAIL,
        "body": {"type": "string"},
    }
)

ALBUM_SCHEMA = _object(
    {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
    }
)

PHOTO_SCHEMA = _object(
    {
        "albumId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "url": URL,
        "thumbnailUrl": URL,
    }
)

TODO_SCHEMA = _object(
    {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "completed": {"type": "boolean"},
    }
)

USER_SCHEMA = _object(
    {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "username": {"type": "string"},
        "email": EMAIL,
        "address": _object(
            {
                "street": {"type": "string"},
                "suite": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"},
                "geo": _object({"lat": {"type": "string"}, "lng": {"type": "string"}}),
            }
        ),
        "phone": {"type": "string"},
        "website": {"type": "string"},
        "company": _object(
            {
                "name": {"type": "string"},
                "catchPhrase": {"type": "string"},
                "bs": {"type": "string"},
            }
        ),
    }
)

SCHEMAS = {
    "posts": POST_SCHEMA,
    "comments": COMMENT_SCHEMA,
    "albums": ALBUM_SCHEMA,
    "photos": PHOTO_SCHEMA,
    "todos": TODO_SCHEMA,
    "users": USER_SCHEMA,
}
