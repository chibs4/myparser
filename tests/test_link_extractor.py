import pytest
import requests

from link_extractor import extract_links
from storage import Storage
from settings import ALLOW_REDIRECT


quotes_url = "https://quotes.toscrape.com/"


@pytest.fixture
def quotes_html() -> str:
    resp = requests.get(quotes_url)
    if resp.status_code != 200:
        pytest.fail(f"Cant connect to {quotes_url}")
    return resp.text


@pytest.fixture
def test_storage() -> Storage:
    return Storage({quotes_url})


def test_link_extractor(quotes_html, test_storage):
    external_link_count = 2
    unique_internal_count = 47
    test_storage.get_external_link()
    extract_links(
        url=quotes_url,
        html=quotes_html,
        storage=test_storage,
    )
    assert "quotes.toscrape.com" in test_storage.main_storage
    internal_links = test_storage.main_storage["quotes.toscrape.com"].internal_links
    external_count = len(test_storage.external_links)
    if ALLOW_REDIRECT:
        assert external_count == external_link_count
    else:
        assert external_count == 0
    assert len(internal_links) == unique_internal_count
    assert "quotes.toscrape.com" in test_storage.domain_queue
