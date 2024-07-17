import aiohttp

from url_validator import validate_url
from storage import get_url_to_scrape, update_after_parse, main_storage, external_links
from storage import Storage
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
    return ["item1", "item2"]


# NOTE: Change test_parser when changing this function
async def old_scrape_page():
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


# NOTE: Change test_parser when changing this function
async def scrape_page(storage: Storage):
    if not (url := storage.get_external_link()):
        domain, url = storage.get_internal_link()
        if not (domain or url):
            logger.debug("No links to scrape")
            return
        elif domain and not url:  # no link left, set finished status
            if storage.is_last_task(domain):
                storage.set_finished_status(domain)
                storage.delete_domain_from_queue(domain)
            return
        storage.increase_crawler_count(domain)
    else:
        domain = validate_url(url)
    if not (html := await make_request(url)):
        return
    result = parse_html(html)
    extract_links(url, html, storage)  # update links with page links
    items = await process_result(result)
    storage.update_or_create_domain_info(
        domain=domain, success_count=len(items), url=url
    )
    storage.update_disallowed_domains(domain)
    storage.decrease_crawler_count(domain)
