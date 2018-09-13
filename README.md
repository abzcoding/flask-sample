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
The system supports multiple users, so the above command can be run as many times as needed with different usernames. Users are stored in the application's database, which by default uses the SQLite engine. An empty database is created in the current folder if a previous database file is not found.

API Documentation
-----------------

The API supported by this application contains one top-level resource:

- `/api/v1.0/todos/`: The collection of todos.

All other resource URLs are to be discovered from the responses returned from the above three.

There are two resource types supported by this API, described in the sections below. Note that this API supports resource representations in JSON format only.

### Resource Collections

All resource collections have the following structure:
```
{
    "urls": [
        [URL 1],
        [URL 2],
        ...
    ],
    "meta": {
        "page": [current_page],
        "pages": [total_page_count],
        "per_page": [items_per_page],
        "total": [total item count],
        "prev": [link to previous page],
        "next": [link to next page],
        "first": [link to first page],
        "last": [link to last page]
    }
}
```
The `urls` key contains an array with the URLs of the requested resources. Note that results are paginated, so not all the resource in the collection might be returned. Clients should use the navigation links in the `meta` portion to obtain more resources.

### Todo Resource

A todo resource has the following structure:
```
{
    "url": [todo URL],
    "name": [todo name],
    "task": [todo task],
    "timestamp": [todo created date]
}
```
When creating or updating a todo resource the `name` and `task` fields needs to be provided. The following example creates a todo resource by sending a `POST` request to the top-level students URL. The `httpie` command line client is used to send this request.
```bash
(venv) $ http --auth <username> POST http://localhost:5000/api/v1.0/todos/ name=buy task="buy groceries"
http: password for <username>@localhost:5000: <password>
HTTP/1.0 201 CREATED
Content-Length: 2
Content-Type: application/json
Date: Thu, 13 Sep 2018 09:58:31 GMT
Location: http://localhost:5000/api/v1.0/todos/1
Server: Werkzeug/0.14.1 Python/3.7.0 

{}
```
The `name` and `task` fields needs to be provided when creating or modifying a todo resource. Note the `Location` header included in the response, which contains the URL of the newly created resource. This URL can now be used to get specific information about this resource:
```bash
(venv) $ http --auth <username> GET http://localhost:5000/api/v1.0/todos/1
http: password for <username>@localhost:5000: <password>
HTTP/1.0 200 OK
Content-Length: 157
Content-Type: application/json
Date: Thu, 13 Sep 2018 09:58:31 GMT
ETag: "c65dfd7eef67b79e15a614c800009830"
Server: Werkzeug/0.14.1 Python/3.7.0 

{
    "name": "buy",
    "task": "buy groceries",
    "timestamp": "Thu, 13 Sep 2018 08:43:26 GMT",
    "url": "http://localhost:5000/api/v1.0/todos/1"
}
```
The todo resource supports `GET`, `POST`, `PUT` and `DELETE` methods.


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

This API supports rate limiting as an optional feature. To use rate limiting the application must have access to a Redis server running on the same host and listening on the default port.

To enable rate limiting change the following line in `config.py`:
```
USE_RATE_LIMITS = True
```
The default configuration limits clients to 5 API calls per 15 second interval. When a client goes over the limit a response with the 429 status code is returned immediately, without carrying out the request. The limit resets as soon as the current 15 second period ends.

When rate limiting is enabled all responses return three additional headers:
```
X-RateLimit-Limit: [period in seconds]
X-RateLimit-Remaining: [remaining calls in this period]
X-RateLimit-Reset: [time when the limits reset, in UTC epoch seconds]
```

Conclusion
----------

I hope you find this example useful. If you have any questions feel free to ask!
