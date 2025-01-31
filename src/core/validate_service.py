from src.db.dao import ApiKeyDao




def valid_existed_keys(website):
    last_id = 0
    while True:
        keys = ApiKeyDao.get_all_keys(website["name"], last_id=last_id)
        if not keys:
            break

        for key in keys:
            result = website["validator"](key.api_key)
            ApiKeyDao.update_one(key.id, result)

        last_id = keys[-1].id