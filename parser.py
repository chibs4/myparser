import aiohttp

from url_validator import validate_url
from storage import get_url_to_scrape, update_after_parse, main_storage, external_links
from link_extractor import extract_links
from utils import logger


async def make_request(url: str) -> str | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
    except Exception as e:
        logger.debug(f"{url} exc:\n {str(e)}")
        return


def parse_html(html: str):
    """Parse finction for every page."""
    return ["item1", "item2"]


async def process_result(result: str | dict):
    """Process parsed result (write to file, db, ...)"""
    return []


# NOTE: Change test_parser when changing this function
async def scrape_page():
    if not (url := get_url_to_scrape()):
        return
    if not (domain := validate_url(url)):
        return
    if not (html := await make_request(url)):
        return
    result = parse_html(html)
    extract_links(
        url, html, main_storage, external_links
    )  # update links with page links
    items = await process_result(result)
    update_after_parse(url, domain, success_count=len(items))
