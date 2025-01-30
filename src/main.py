import argparse
import logging
import rich

from src.configs import LANGUAGES
from src.core import APIKeyLeakageScanner
from src.logging_utils import init_logging

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)


def main(from_iter: int | None = None, check_existed_keys_only: bool = False, languages: list | None = None):
    if languages is None:
        languages = LANGUAGES.copy()
    leakage = APIKeyLeakageScanner("github.db", languages)

    if not check_existed_keys_only:
        leakage.login_to_github()
        leakage.search(from_iter=from_iter)

    leakage.update_existed_keys()
    leakage.deduplication()
    keys = leakage.all_available_keys()

    rich.print(f"🔑 [bold green]Available keys ({len(keys)}):[/bold green]")
    for key in keys:
        rich.print(f"[bold green]{key[0]}[/bold green]")


if __name__ == "__main__":
    init_logging("main")
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-iter", type=int, default=None,
                        help="Start from the specific iteration")
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode, otherwise INFO mode. Default is False (INFO mode)",
    )
    parser.add_argument(
        "-ceko",
        "--check-existed-keys-only",
        action="store_true",
        default=False,
        help="Only check existed keys",
    )
    parser.add_argument(
        "-l",
        "--languages",
        nargs="+",
        default=LANGUAGES,
        help="Languages to search",
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    main(
        from_iter=args.from_iter,
        check_existed_keys_only=args.check_existed_keys_only,
        languages=args.languages,
    )
