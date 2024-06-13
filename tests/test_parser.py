import pytest
import asyncio

from parser import (
    get_url_to_scrape,
    validate_url,
    make_request,
    parse_html,
    process_result,
)
from storage import (
    main_storage,
    update_after_parse,
    disallowed_domains,
    internal_links_queue,
    external_links,
)
from link_extractor import extract_links

ip_url = "https://browserleaks.com/ip"


@pytest.mark.asyncio
async def test_scrape_page():
    if not (url := get_url_to_scrape()):
        pytest.fail("Error getting url from external storage.")
    assert len(external_links) == 0
    if not (domain := validate_url(url)):
        pytest.fail(f"Url extractor error. url: {url}")
    if not (html := await make_request(url)):
        pytest.fail("Error getting html from site")
    result = parse_html(html)
    assert len(result)
    assert not external_links
    extract_links(
        url, html, main_storage, external_links
    )  # tested in test_extract_links
    items = await process_result(result)
    update_after_parse(url, domain, success_count=len(items))
    assert len(disallowed_domains) == 1
    assert domain in main_storage
    domain_info = main_storage[domain]
    assert domain_info.num_of_crawlers == 0
    assert domain_info.success_count == len(items)


@pytest.mark.asyncio
async def second_run_test():
    """After first test parser should take internal link of ip_url."""
    assert len(external_links) == 0
    if not (url := get_url_to_scrape()):
        pytest.fail("Error getting url from internal storage.")
    assert len(internal_links_queue) == 1
    if not (domain := validate_url(url)):
        pytest.fail(f"Url extractor error. url: {url}")
    assert domain in main_storage
    domain_info = main_storage[domain]
    old_item_count = domain_info.success_count
    assert domain_info.num_of_crawlers == 1
    if not (html := await make_request(url)):
        pytest.fail("Error getting html from site (2)")
    result = parse_html(html)
    assert len(result)
    extract_links(
        url, html, main_storage, external_links
    )  # tested in test_extract_links
    items = await process_result(result)
    update_after_parse(url, domain, success_count=len(items))
    assert domain_info.success_count == old_item_count + len(items)
    assert domain_info.num_of_crawlers == 0
    rel_url = url.split(domain)[-1]
    assert len(domain_info.crawled_links == 1) and rel_url in domain_info.crawled_links
    assert rel_url not in domain_info.internal_links
