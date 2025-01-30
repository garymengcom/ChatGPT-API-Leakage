import logging
import rich

from src.configs import WEBSITES
from src.core import APIKeyLeakageScanner
from src.db.dao import ApiKeyDao
from src.logging_utils import init_logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


if __name__ == "__main__":
    init_logging("api_key_leakage_scanner")
    for website in WEBSITES:
        service = APIKeyLeakageScanner(website)

        service.login_to_github()
        service.search()

        valid_count = ApiKeyDao.get_valid_key_count(website["name"])
        rich.print(f"🔑 ({website['name']})[bold green]Available keys ({valid_count}):[/bold green]")