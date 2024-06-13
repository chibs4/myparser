import logging

logger = logging.Logger(name="main")


def is_internal(domain: str, link: str) -> bool:
    """Check if link internal or external."""
    if domain in link or link.startswith("/"):
        return True
    return False
