from pydantic import BaseModel, conint
from collections import deque
from typing import Iterable

from utils import logger
from settings import CRAWLERS_PER_DOMAIN, START_URLS
from url_validator import validate_urls
from utils import is_internal


class DomainInfo(BaseModel):
    num_of_crawlers: conint(le=CRAWLERS_PER_DOMAIN) = 0
    success_count: int = 0
    internal_links: set[str] = set()
    crawled_links: set[str] = set()
    finished: bool = False


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


class Storage:
    # Main storage for crawler while its running. Stored as domain:DomainInfo.
    main_storage: dict[str, DomainInfo] = {}
    # Queue of domains
    domain_queue = deque([])
    # Parsed or disallowed set
    disallowed_domains: set = set()

    def __init__(self, start_urls: set = START_URLS):
        # Shared external link set
        self.external_links: deque = deque(start_urls)

    def _create_domain_info(
        self,
        domain: str,
        success_count: int = 0,
        crawled_link: str = "/",
        links: set[str] = set(),
    ):
        self.main_storage[domain] = DomainInfo(
            success_count=success_count,
            internal_links=links,
            crawled_links={crawled_link},
            num_of_crawlers=1,
        )
        self._add_domain_to_domain_queue(domain)

    def _update_domain_info(
        self,
        domain: str,
        num_of_crawlers: int = None,
        success_count: int = None,
        links: set[str] = None,
        crawled_link: str = None,
        finished: bool = False,
    ):
        """Update DomainInfo and add it to queue if it still has unsraped links."""
        domain_info = self.main_storage.get(domain, None)
        if not domain_info:
            raise KeyError(f"Update domain {domain}: domain not found")
        if num_of_crawlers:
            domain_info.num_of_crawlers += num_of_crawlers
        if success_count:
            domain_info.success_count += success_count
        if crawled_link:
            rel_link = self._get_relative_url(domain, crawled_link)
            domain_info.crawled_links.add(rel_link)
        if links:
            allowed_links = links.difference(domain_info.crawled_links)
            domain_info.internal_links.update(allowed_links)
        if finished:
            domain_info.finished = finished

    def update_or_create_domain_info(
        self,
        domain: str,
        success_count: int,
        links: set[str] = None,
        url: str = "/",
    ):
        """Should be called after every succesfull crawl on address rel_url."""
        try:
            self._update_domain_info(
                domain,
                success_count=success_count,
                links=links,
                crawled_link=url,
            )
        except KeyError:
            self._create_domain_info(
                domain,
                success_count=success_count,
                links=links,
                crawled_link=url,
            )

    def is_last_task(self, domain) -> bool:
        return self.main_storage[domain].num_of_crawlers == 0

    def set_finished_status(self, domain: str):
        self._update_domain_info(domain, finished=True)
        self.update_disallowed_domains(domain)

    def increase_crawler_count(self, domain: str):
        if domain in self.main_storage:
            self._update_domain_info(domain, num_of_crawlers=1)

    def decrease_crawler_count(self, domain: str):
        if domain in self.main_storage:
            self._update_domain_info(domain, num_of_crawlers=-1)

    def _get_domain_from_domain_queue(self) -> str | None:
        if self.domain_queue:
            return self.domain_queue[0]

    def delete_domain_from_queue(self, domain):
        self.domain_queue.remove(domain)

    def _add_domain_to_domain_queue(self, domain: str):
        self.domain_queue.append(domain)

    def _get_domain_internal_link(self, domain: str) -> str | None:
        domain_info = self.main_storage.get(domain, None)
        if not domain_info:
            raise KeyError(f"Get domain {domain}: domain not found")
        if not domain_info.internal_links:
            return
        return domain_info.internal_links.pop()

    def _make_full_url(self, domain: str, rel_url: str) -> str:
        if rel_url.startswith("/"):
            return "https://" + domain + rel_url
        else:
            return rel_url

    def _get_relative_url(self, domain: str, url: str) -> str:
        if domain in url:
            return url.split(domain)[-1]
        else:
            return url

    def get_internal_link(self) -> tuple[str | None, str | None]:
        """Returns tuple of domain and full link. If domain has no link left, finished stastus should be wrote."""
        domain = self._get_domain_from_domain_queue()
        if not domain:
            return None, None
        rel_link = self._get_domain_internal_link(domain)
        if not rel_link:
            return domain, None
        full_link = self._make_full_url(domain, rel_link)
        return domain, full_link

    def update_external_links(self, links: set[str]):
        domains = validate_urls(links)
        for link, domain in zip(links, domains):
            if domain not in self.disallowed_domains:
                self.external_links.append(link)

    def get_external_link(self) -> str | None:
        if self.external_links:
            return self.external_links.popleft()

    def update_disallowed_domains(self, domain: str):
        self.disallowed_domains.add(domain)


storage = Storage()
