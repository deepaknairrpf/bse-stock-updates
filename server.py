import json

import cherrypy
import cherrypy_cors
import redis
import os
from equity_download import EquityDownloader
import  datetime

redis_conn = redis.StrictRedis(host='localhost', port=6379, charset="utf-8", decode_responses=True)
redis_sorted_set_namespace = "stocks_set"
redis_latest_scrapped_date_key = "latest_scrapped_date"
redis_last_refreshed_date_time_key = "last_refreshed_datetime"

STOCK_DATA_COLLECTION_PERIOD = 3600 * 12


STATIC_DIR = os.path.join(os.path.abspath("."), u"static")

class StockDataScrapper:

    @cherrypy.expose
    def index(self):
        """Index route, returning the index.html file with associated CSS and js scripts."""
        return open(os.path.join(STATIC_DIR, u'index.html'))

    @cherrypy.expose
    def fetch_data(self, page_start, page_end, _):
        """List route to list stock data from redis sorted in descending order of their no. of trades.

        Args:
            page_start <int>: Start index of pagination.
            page_end <int>: Last index of pagination.
            _ <str> : CORS id

        Returns:
            JSON: A JSON representation of the corresponding stock details..
        """
        return_dict = {
            "data": []
        }
        equity_list = redis_conn.zrange(redis_sorted_set_namespace, page_start, page_end, desc=True)
        if not equity_list:
            reload_redis_with_latest_data()
            equity_list = redis_conn.zrange(redis_sorted_set_namespace, page_start, page_end, desc=True)
        return_dict["latest_date"] = redis_conn.get(redis_latest_scrapped_date_key)
        for equity_name in equity_list:
            equity_data = redis_conn.hgetall(equity_name)
            return_dict["data"].append(equity_data)
        print(json.dumps(return_dict))  # TODO (Deepak): Replace with logger
        return json.dumps(return_dict)

    @cherrypy.expose
    def search(self, title):
        """Search route to search for a specific stock data from redis using the name of the stock as the key.

        Searches for the key in a Redis Hashmap.

         Args:
             title <str>: String representation of the name of the stock.

         Returns:
             JSON: A JSON representation of the fetched stock. Returns an empty object if stock
             info isn't available.
         """
        equity_data = redis_conn.hgetall(title)
        return json.dumps(equity_data)

    @cherrypy.expose
    def last_scrapped_date(self):
        date_dict = {
            "last_scrapped_date": redis_conn.get(redis_latest_scrapped_date_key),
            "last_refreshed_datetime": redis_conn.get(redis_last_refreshed_date_time_key)
        }
        return json.dumps(date_dict)

def reload_redis_with_latest_data():
    """Intended to be a periodic task to refresh redis db with latest stock info from BSE website.
    Reloads the Redis sorted set and the hash map with latest data.
     """
    equity_data = EquityDownloader.get_equity_data()
    data_url = EquityDownloader.get_href_for_latest_equity_data()
    latest_date = EquityDownloader.get_corresponsding_date_for_href(data_url)
    redis_conn.set(redis_latest_scrapped_date_key, latest_date)
    redis_conn.set(redis_last_refreshed_date_time_key, datetime.datetime.now().strftime("%H:%M %d/%m/%y"))

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
