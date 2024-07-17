import pytest

from parser import (
    validate_url,
    make_request,
    parse_html,
    process_result,
)

from storage import Storage
from link_extractor import extract_links

ip_url = "https://browserleaks.com/ip"


@pytest.fixture
def test_storage() -> Storage:
    return Storage({ip_url})


@pytest.mark.asyncio
async def test_scrape_page(test_storage: Storage):
    if not (url := test_storage.get_external_link()):
        pytest.fail("Error getting url from external test_storage.")
        assert len(test_storage.external_links) == 0
    if not (domain := validate_url(url)):
        pytest.fail(f"Url extractor error. url: {url}")
    if not (html := await make_request(url)):
        pytest.fail("Error getting html from site")
    result = parse_html(html)
    assert len(result)
    assert not test_storage.external_links
    extract_links(url, html, test_storage)  # tested in test_extract_links
    items = await process_result(result)
    test_storage.update_or_create_domain_info(domain, success_count=len(items))
    test_storage.update_disallowed_domains(domain)
    test_storage.decrease_crawler_count(domain)
    assert len(test_storage.disallowed_domains) == 1
    assert domain in test_storage.main_storage
    domain_info = test_storage.main_storage[domain]
    assert domain_info.num_of_crawlers == 0
    assert domain_info.success_count == len(items)
    assert "browserleaks.com" in test_storage.domain_queue


@pytest.mark.asyncio
async def second_run_test(test_storage: Storage):
    """After first test parser should take internal link of ip_url."""
    assert len(test_storage.external_links) == 0
    domain, url = test_storage.get_internal_link()
    if not (domain and url):
        pytest.fail("Error getting url from internal test_storage.")
    assert len(test_storage.domain_queue) == 1
    if not (domain := validate_url(url)):
        pytest.fail(f"Url extractor error. url: {url}")
    assert domain in test_storage.main_storage
    domain_info = test_storage.main_storage[domain]
    old_item_count = domain_info.success_count
    assert domain_info.num_of_crawlers == 1
    if not (html := await make_request(url)):
        pytest.fail("Error getting html from site (2)")
    result = parse_html(html)
    assert len(result)
    extract_links(url, html, test_storage)  # tested in test_extract_links
    assert domain_info.num_of_crawlers == 1
    items = await process_result(result)
    test_storage.update_or_create_domain_info(domain, success_count=len(items))
    test_storage.update_disallowed_domains(domain)
    test_storage.decrease_crawler_count(domain)
    assert domain_info.success_count == old_item_count + len(items)
    assert domain_info.num_of_crawlers == 0
    rel_url = url.split(domain)[-1]
    assert len(domain_info.crawled_links == 1) and rel_url in domain_info.crawled_links
    assert rel_url not in domain_info.internal_links
    assert "browserleaks.com" in test_storage.domain_queue
