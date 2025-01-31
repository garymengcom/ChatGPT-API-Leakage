import logging

from src.core.configs import WEBSITES
from src.core.validate_service import valid_existed_keys
from src.core.logging_utils import init_logging


if __name__ == "__main__":
    init_logging("validation")
    for website in WEBSITES:
        valid_existed_keys(website)
        logging.info("🔑 [%s]Finished validating existed keys", website["name"])

    logging.info("All done")