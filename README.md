Sample RESTful Web Service Using Flask & SQLAlchemy
===================================================

a bare minimum rest api with couple of useful features.

Requirements
------------

To install and run this application you need:

- Python 2.7 or 3.3+
- virtualenv
- git

Installation
------------
The commands below install the application and its dependencies:
```bash
git clone https://github.com/abzcoding/flask-sample.git
cd flask-Sample
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

Unit Tests
----------

To ensure that your installation was successful you can run the unit tests:

```bash
python manage.py test
```

User Registration
-----------------

The API can only be accessed by authenticated users. New users can be registered
with the application from the command line:
```bash
python manage.py adduser <username>
```

Using Token Authentication
--------------------------
                         
The default configuration uses username and password for request authentication. To switch to token based authentication the configuration stored in `config.py` must be edited. In particular, the line that begins with `USE_TOKEN_AUTH` must be changed to:     
```
USE_TOKEN_AUTH = True
```
After this change restart the application for the change to take effect.                                                                   With this change authenticating using username and password will not work anymore. Instead an authentication token must be requested:
```bash
http --auth <username> GET http://localhost:5000/auth/request-token
```
The returned token must be sent as authentication for all requests into the API:
```bash
http --auth eyJhbGciOiJIUzI1NiIsImV4cCI12837281MTM5NjU3NzkzNSwiaWF0IjoxMzk2NTc0MzM1fQ.eyJpZCI6MX0.8XFUzlGz5XPGJp0weoOXy6avwr7OS1ojMbJYpBvw42I: GET http://localhost:5000/api/v1.0/sample_api/
```

HTTP Caching
------------

The different API endpoints are configured to respond using the appropriate caching directives. The `GET` requests return an `ETag` header that HTTP caches can use with the `If-Match` and `If-None-Match` headers.

The `GET` request that returns the authentication token is not supposed to be cached, so the response includes a `Cache-Control` directive that disables caching.

Rate Limiting
-------------

This API supports rate limiting as an optional feature. To use rate limiting the application must have access to a Redis server running on the same host and listening on the defa
ult port.

To enable rate limiting change the following line in `config.py`:
```
USE_RATE_LIMITS = True
```
The default configuration limits clients to 5 API calls per 15 second interval. When a client goes over the limit a response with the 429 status code is returned immediately, wit
hout carrying out the request. The limit resets as soon as the current 15 second period ends.

When rate limiting is enabled all responses return three additional headers:
```
X-RateLimit-Limit: [period in seconds]
X-RateLimit-Remaining: [remaining calls in this period]
X-RateLimit-Reset: [time when the limits reset, in UTC epoch seconds]
```

Conclusion
----------

I hope you find this example useful. If you have any questions feel free to ask!
