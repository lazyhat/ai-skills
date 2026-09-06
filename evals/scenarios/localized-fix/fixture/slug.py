import re


def normalize_slug(value: str) -> str:
    return re.sub(r"\s+", "-", value.lower())
