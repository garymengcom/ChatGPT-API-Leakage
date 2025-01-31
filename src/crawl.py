import logging
import rich

from src.core.configs import WEBSITES
from src.core.crawler_service import APIKeyLeakageScanner
from src.db.dao import ApiKeyDao
from src.core.logging_utils import init_logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


if __name__ == "__main__":
    init_logging("crawling")
    for website in WEBSITES:
        service = APIKeyLeakageScanner(website)

        service.login_to_github()
        service.search()

        valid_count = ApiKeyDao.get_valid_key_count(website["name"])
        rich.print(f"🔑 ({website['name']})[bold green]Available keys ({valid_count}):[/bold green]")