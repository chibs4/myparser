import pytest
import asyncio
import logging

from crawler_process import ProcessHandler
from parser import scrape_page
from storage import Storage
import settings
from utils import logger

settings.ALLOW_REDIRECT = False


quotes_url = "https://quotes.toscrape.com/"


@pytest.fixture
def test_storage() -> Storage:
    return Storage({quotes_url})


@pytest.mark.asyncio
async def test_processes(test_storage):
    async with ProcessHandler() as ph:
        while True:
            await asyncio.sleep(0.1)
            await ph.create_task(scrape_page, storage=test_storage)
            if "quotes.toscrape.com" in test_storage.main_storage:
                domain_info = test_storage.main_storage["quotes.toscrape.com"]
                if domain_info.finished:
                    break
    assert domain_info.num_of_crawlers == 0
    assert not domain_info.internal_links
    assert len(domain_info.crawled_links) > 1
    logger.info(f"Crawled {len(domain_info.crawled_links)} links")
    logger.debug(domain_info.crawled_links)
