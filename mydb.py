import pandorabot


def get_engine_url():
    engine_url = (f'mysql+pymysql://'
                  f'{pandorabot.db_info[2]}:{pandorabot.db_info[3]}@{pandorabot.db_info[0]}/{pandorabot.db_info[1]}')
    return engine_url
