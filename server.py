import cherrypy
from equity_download import EquityDownloader
import redis


redis_conn = redis.StrictRedis(host='localhost', port=6379)
redis_sorted_set_namespace = "stocks_set"

STOCK_DATA_COLLECTION_PERIOD = 3600 * 24


class StockDataScrapper:

    @cherrypy.expose
    def index(self):
        equity_list = redis_conn.zrange(redis_sorted_set_namespace, 0, -1)
        if not equity_list:
            reload_redis_with_latest_data()
            equity_list = redis_conn.zrange(redis_sorted_set_namespace, 0, -1)

        for equity_name in equity_list:
            equity_data = redis_conn.hgetall(equity_name)
            print(equity_data)
        return "Hello World"

    @cherrypy.expose
    def search(self, title):
        equity_data = redis_conn.hgetall(title)
        print(equity_data)


def reload_redis_with_latest_data():
    equity_data = EquityDownloader.get_equity_data()
    for data in equity_data:
        redis_conn.zadd(redis_sorted_set_namespace, float(data.no_of_trades), data.name)
        redis_conn.hmset(data.name, data.get_stock_details_as_dict())


if __name__ == "__main__":
    cherrypy.engine.housekeeper = cherrypy.process.plugins.BackgroundTask(
        STOCK_DATA_COLLECTION_PERIOD,
        reload_redis_with_latest_data
    )
    cherrypy.engine.housekeeper.start()
    cherrypy.quickstart(StockDataScrapper())