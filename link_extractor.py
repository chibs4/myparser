from bs4 import BeautifulSoup
from collections import deque

from url_validator import validate_url
from storage import DomainInfo, disallowed_domains, internal_links_queue
from utils import is_internal


def extract_links(
    url: str,
    html: str,
    main_storage: dict[str, DomainInfo],
    external_link_storage: deque[list],
):
    """Finds links in html on domain and separates them into two groups:
    internal and external."""
    domain = validate_url(url)
    external, internal = set(), set()
    soup = BeautifulSoup(html, "lxml")
    all_links = soup.find_all("a")
    for link in all_links:
        href = link["href"]
        if is_internal(domain, href):
            internal.add(href)
        else:
            external.add(href)
    # adding sets to storages
    if external:
        allowed_external = external.difference(disallowed_domains)
        external_link_storage += allowed_external
    if internal:
        if domain in main_storage:
            allowed_internal = internal.difference(main_storage[domain].crawled_links)
            main_storage[domain].internal_links.update(allowed_external)
        else:
            new_domain = DomainInfo(internal_links=internal)
            main_storage[domain] = new_domain
        internal_links_queue.append(domain)
