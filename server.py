import cherrypy
from equity_download import EquityDownloader
import redis


redis_conn = redis.StrictRedis(host='localhost', port=6379)
namespace = "stocks"

class HelloWorld:

    @cherrypy.expose
    def index(self):
        equity_data = EquityDownloader.get_equity_data()
        for data in equity_data:
            import ipdb; ipdb.set_trace()
            print(redis_conn.zadd(namespace, float(data.no_of_trades), data.name))
        return "Hello World"

if __name__ == "__main__":
    cherrypy.quickstart(HelloWorld())