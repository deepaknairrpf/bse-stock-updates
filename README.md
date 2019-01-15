# Daily BSE Stock Updates..
A simple cherrypy web app which displays latest BSE equity data stored in a redis data store.

## Backend
-------------------------------------------
### Redis
The webapp stores the ticker symbol or the name of the stock in a sorted set and assigns the no. of trades for that particular stock as the score. This allows listing the stocks in descending order of no. of trades very efficient, giving us the most popular stocks by range in O(range) time.

The webapp then maps the name of the stock to it's corresponding data in a Redis Hash Map which allows search in O(1).
Therefore, sorted set and the hash map works in tandem to list and search through stocks.

### Cherrypy
Cherrypy is a light-weight webapp framework. The application server is written using cherrypy which communicates with Redis, the primary data source for this app.
Background tasks are written in Cherrypy which checks every 12 hrs whether updated stock information is available from BSE website and extracts the zip file and converts the csv into the above mentioned Redis data structures, if available.
BeautifulSoup was used to easily parse the html page.

## Frontend
-----------------------------------------------
A basic HTML5 and CSS3 page which provides a data table functionality with pagination and a search bar using jquery and ajax for asynchronous HTTP requests.
Pic:

#### Future improvements
------------------------------------------------
1. RESTify all routes.
2. Loadtest the efficiency between hitting Redis db for every paginated request and hitting the search route to retrieve a stock item from the Redis hash versus caching the entire response on the frontend and searching in it. The former is assumed to be faster as the number of stock objects increase and the former is what that's implemented.
3. Integrate test coverage tools.
4. Make the app work for an arbitrary date input from the user.
5. Implement different types of filters that can be performed efficiently on Redis. 
   Ex:- Fetch all stocks of SC_GROUP A and SC_TYPE Q.
   
