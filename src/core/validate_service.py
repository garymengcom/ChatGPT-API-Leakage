import logging

from src.db.dao import ApiKeyDao




def valid_existed_keys(website):
    last_id = 0
    batch_size = 10
    while True:
        keys = ApiKeyDao.get_all_keys(website["name"], last_id=last_id, batch_size=batch_size)
        if not keys:
            break

        for key in keys:
            result = website["validator"](key.api_key)
            ApiKeyDao.update_one(key.id, result)

        first_id = keys[0].id
        last_id = keys[-1].id
        logging.info(f"🔑 Validated [{first_id} - {last_id}] keys")