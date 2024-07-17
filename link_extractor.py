from bs4 import BeautifulSoup
from url_validator import validate_url

# from storage import DomainInfo, disallowed_domains, internal_links_queue
from utils import is_internal
from storage import Storage
from settings import ALLOW_REDIRECT


def extract_links(url: str, html: str, storage: Storage):
    """Finds links in html on domain and separates them into two groups:
    internal and external."""
    domain = validate_url(url)
    external, internal = set(), set()
    soup = BeautifulSoup(html, "lxml")
    all_links = soup.find_all("a")
    for link in all_links:
        href = link["href"]
        if is_internal(domain, href):
            if domain in href:
                href = href.split(domain)[-1]
            internal.add(href)
        else:
            external.add(href)
    # adding sets to storages
    if external and ALLOW_REDIRECT:
        storage.update_external_links(external)
    if internal:
        storage.update_or_create_domain_info(domain, links=internal, success_count=0)
