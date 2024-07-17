import logging

logging.basicConfig(
    level="DEBUG", format="%(taskName)s | %(asctime)s | %(levelname)s %(message)s"
)


# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
def add_colors_to_log_levels():
    colors = {
        logging.ERROR: 31,
        logging.WARNING: 33,
        logging.INFO: 32,
        logging.DEBUG: 96,
    }
    for level_name, color in colors.items():
        logging.addLevelName(
            level_name, f"\033[{color}m{logging.getLevelName(level_name)}\033[1;0m"
        )


add_colors_to_log_levels()
logger = logging.getLogger(name="main")


def is_internal(domain: str, link: str) -> bool:
    """Check if link internal or external."""
    if domain in link or link.startswith("/"):
        return True
    return False
