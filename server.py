import json

import cherrypy
import cherrypy_cors
import redis
import os
from equity_download import EquityDownloader

redis_conn = redis.StrictRedis(host='localhost', port=6379, charset="utf-8", decode_responses=True)
redis_sorted_set_namespace = "stocks_set"

STOCK_DATA_COLLECTION_PERIOD = 3600 * 24


STATIC_DIR = os.path.join(os.path.abspath("."), u"static")

class StockDataScrapper:

    @cherrypy.expose
    def index(self):
        return open(os.path.join(STATIC_DIR, u'index.html'))

    @cherrypy.expose
    def fetch_data(self, page_start, page_end, _):
        return_dict = {
            "data": []
        }
        equity_list = redis_conn.zrange(redis_sorted_set_namespace, page_start, page_end, desc=True)
        if not equity_list:
            reload_redis_with_latest_data()
            equity_list = redis_conn.zrange(redis_sorted_set_namespace, 0, -1)

        for equity_name in equity_list:
            equity_data = redis_conn.hgetall(equity_name)
            return_dict["data"].append(equity_data)
        print(json.dumps(return_dict))
        return json.dumps(return_dict)

    @cherrypy.expose
    def search(self, title):
        equity_data = redis_conn.hgetall(title)
        return json.dumps(equity_data)


def reload_redis_with_latest_data():
    equity_data = EquityDownloader.get_equity_data()
    for data in equity_data:
        redis_conn.zadd(redis_sorted_set_namespace, float(data.no_of_trades), data.name)
        redis_conn.hmset(data.name, data.get_stock_details_as_dict())


def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


if __name__ == "__main__":
    cherrypy_cors.install()
    config = {
        '/': {
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'cors.expose.on': True,
        },
        '/static':
            {'tools.staticdir.on': True,
             'tools.staticdir.dir': STATIC_DIR,
             }
    }
    cherrypy.engine.housekeeper = cherrypy.process.plugins.BackgroundTask(
        STOCK_DATA_COLLECTION_PERIOD,
        reload_redis_with_latest_data
    )
    cherrypy.config.update({'tools.CORS.on': True,})
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.engine.housekeeper.start()
    cherrypy.quickstart(StockDataScrapper(), config=config)
