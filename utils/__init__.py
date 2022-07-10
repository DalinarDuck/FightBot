import ujson
import aiohttp

#config file
with open('config.json') as file:
    config_file = ujson.load(file)


