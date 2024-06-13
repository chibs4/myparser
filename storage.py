from pydantic import BaseModel, conint
from collections import deque
from typing import Iterable

from utils import logger
from settings import CRAWLERS_PER_DOMAIN, START_URLS
from utils import is_internal


class DomainInfo(BaseModel):
    num_of_crawlers: conint(le=CRAWLERS_PER_DOMAIN) = 0
    success_count: int = 0
    internal_links: set[str] = set()
    crawled_links: set[str] = set()


# Main storage for crawler while its running. Stored as domain:DomainInfo.
main_storage: dict[str, DomainInfo] = {}
# Queue of domains
internal_links_queue = deque([])


# Shared external link set
def create_external_links_queue(start_urls: Iterable) -> deque:
    return deque(start_urls)


external_links = create_external_links_queue(START_URLS)
# external_links: deque = deque(START_URLS)
# Parsed or disallowed set
disallowed_domains: set = set()


def get_url_to_scrape() -> str | None:
    if external_links:
        return external_links.popleft()
    elif internal_links_queue:
        domain = internal_links_queue.popleft()
        update_process_count(domain)
        if rel_link := get_relative_url(domain):
            internal_links_queue.append(domain)
            return rel_link
    else:
        logger.warn("no links to scrape")
        return


def get_relative_url(domain) -> str | None:
    domain_info = main_storage.get(domain, None)
    if not (domain_info or domain_info.internal_links):
        return
    rel_link = domain_info.internal_links.pop()
    return "https://" + domain + rel_link


def update_process_count(domain, is_add: bool = True):
    domain_info = main_storage[domain]
    if is_add:
        domain_info.num_of_crawlers += 1
    else:
        domain_info.num_of_crawlers -= 1


def update_internal_link(url: str, domain: str, success_count: int):
    if domain in main_storage:
        old_domain: DomainInfo = main_storage[domain]
        old_domain.success_count += success_count
        rel_url = url.split(domain)[-1]
        old_domain.crawled_links.add(rel_url)
    else:
        main_storage[domain] = DomainInfo(success_count=success_count)


def update_after_parse(url: str, domain: str, success_count: int):
    if is_internal(url, domain):
        update_internal_link(url, domain, success_count)
        update_process_count(domain, is_add=False)
    else:
        disallowed_domains.add(domain)
