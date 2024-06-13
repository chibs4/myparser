import pytest
import requests
from collections import deque

from link_extractor import extract_links


quotes_url = "https://quotes.toscrape.com/"


@pytest.fixture
def quotes_html() -> str:
    resp = requests.get(quotes_url)
    if resp.status_code != 200:
        pytest.fail(f"Cant connect to {quotes_url}")
    return resp.text


@pytest.fixture
def test_storage() -> dict:
    return {}


@pytest.fixture
def test_external_links_storage() -> deque:
    return deque([])


def test_link_extractor(quotes_html, test_storage, test_external_links_storage):
    external_link_count = 2
    unique_internal_count = 47
    extract_links(
        url=quotes_url,
        html=quotes_html,
        main_storage=test_storage,
        external_link_storage=test_external_links_storage,
    )
    assert "quotes.toscrape.com" in test_storage
    internal_links = test_storage["quotes.toscrape.com"].internal_links
    assert len(test_external_links_storage) == external_link_count
    assert len(internal_links) == unique_internal_count
